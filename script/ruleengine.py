from abc import abstractmethod
from typing import ClassVar, Any, List, Dict
import logging
import inspect

class Rule:
    """Base class for rules."""

    @abstractmethod
    def when(context: 'RuleEngine.Context', **kwargs) -> bool:
        """
        Matches the parameters of the rule from the context and checks whether
        the rule is eligible for firing.

        The first argument is fixed: the context for the rule execution.
        The additional (optional) arguments can be used to match variables
        from the rule context based on name and type. The name and type of 
        the arguments has to match a variable in the context in order for
        the rule to be eligible.

        Example: def when(context: RuleEngine.Context, a: int, b: Any, c: None)
          - There has to be an int variable called "a" in the context
          - There has to be a variable of any type in the context called "b"
          - There must not be a variable called "c" in the context.

        If the parameter list is successfully matched to the context, this 
        method is called by the rule engine. The return value indicates whether 
        the rule is eligible for firing.
        """
        raise NotImplementedError()

    @abstractmethod
    def then(context: 'RuleEngine.Context', **kwargs) -> None:
         """
         Performs the action of the rule, for example: modifies the context, 
         or causes a side-effect.

         This method is called by the rule engine during rule execution if
         the rule is eligible for firing. The parameter list is depending
         on the parameter list of the when(...) method. The context is always
         passed, the necessary additional arguments can be captured with the
         same name that was used in when(...) during parameter matching. Not
         all matched arguments has to be specified (use **kwargs to swallow
         the unused matched parameters). 
         """
         raise NotImplementedError()

class RuleEngine:
    """Rule engine for evaluating rules."""
    
    """List of registered rule classes."""
    rules: ClassVar[list[Rule]] = []

    logger: ClassVar[logging.Logger] = logging.getLogger('RuleEngine')
    
    class Context:
        """Context class for passing information to and between rules."""

        def __init__(self, attributes: dict = None):
            """Initializes the rule Context."""
            self._attributes = {}
            self._changed_attributes = set()
            self._flags = set()
            self.actions = []

            if isinstance(attributes, Dict):
                self.update(attributes)
        
        ## Handling attributes
        ## ===================

        def update(self, key_or_dict: str | dict, value: Any = None):
            """Updates the value of the specified variable."""
            
            def is_value_changed_or_new(_key: str, _value: Any):
                return _key not in self._attributes \
                       or (_key in self._attributes 
                           and self._attributes[_key] != _value)

            if isinstance(key_or_dict, str):
                if is_value_changed_or_new(key_or_dict, value):
                    self._changed_attributes.add(key_or_dict)
                    self._attributes[key_or_dict] = value

            elif isinstance(key_or_dict, Dict):
                for key, dict_value in key_or_dict.items():
                    if is_value_changed_or_new(key, dict_value):
                        self._changed_attributes.add(key)
                        self._attributes[key] = dict_value

            else:
                raise AssertionError(f'Wrong parameters: {type(key_or_dict)}.')
            
        def get(self, key, default = None):
            return self._attributes.get(key, default)
        
        def has_attribute(self, key):
            return key in self._attributes

        def changed_attributes(self) -> set[str]:
            """Queries changed attributes since the last invocation."""
            changed_attributes = self._changed_attributes.copy()
            self._changed_attributes.clear()
            return changed_attributes

        def has_changed(self):
            """Queries whether there are any changed attributes without clearing them."""
            return len(self._changed_attributes) != 0
        
        ## Handling flags
        ## ==============

        def has_flag(self, flag: str) -> bool:
            """Queries whether the specified flag is set."""
            return flag in self._flags 

        def set_flag(self, flag: str) -> None:
            """Sets the specified flag."""
            self._flags.add(flag)

        def reset_flag(self, flag: str) -> None:
            """Resets the specified flag."""
            self._flags.discard(flag)

        def clear(self):
            """Deletes all flags at attributes."""
            self.__init__()

    @classmethod
    def register_rule(cls, rule_class) -> None:
        """Registers a rule within the rule engine."""
        cls.rules.append(rule_class)

    @classmethod
    def execute_rules(cls, context: Context | Dict) -> Context:
        """Executes the rules."""

        if isinstance(context, Dict):
            context = RuleEngine.Context(context)

        changed_attributes = context.changed_attributes()
        cls.logger.setLevel(logging.DEBUG)

        def gather_rule_args(rule_class):
            """Gathers the arguments required by the specified rule from the context."""
            return {arg_name: context.get(arg_name) if arg_type is not None else None
                    for arg_name, arg_type in rule_class.required_args.items()}

        def can_rule_fire(rule_class):
            """Determines whether the specified rule is eligible for execution."""
            return rule_class.has_required_arguments(context) \
                   and rule_class.has_argument_changed(changed_attributes) \
                   and rule_class.when(context, **gather_rule_args(rule_class))

        cls.logger.debug('====== Rule engine started ======')
        while changed_attributes or context.actions:
            cls.logger.debug(f'Iteration, changed_attributes={changed_attributes}')
            agenda = [rule for rule in cls.rules if can_rule_fire(rule)]
            agenda.sort(key=lambda rule: rule.priority, reverse=True)
            cls.logger.debug(f'Agenda sorted, agenda={[rule.__name__ for rule in agenda]}')
            for rule in agenda:
                rule.then(context, **gather_rule_args(rule))

            changed_attributes = context.changed_attributes()

        return context

def accepts_keywords(*allowed_keywords):
    """Searches the keyword arguments of another decorator for not allowed keywords."""
    def decorator(decorator_func):
        def wrapper(*args, **kwargs):
            for kwarg in kwargs:
                if kwarg not in allowed_keywords:
                    raise ValueError(f'Keyword "{kwarg}" is not allowed in @{decorator_func.__name__}')
            return decorator_func(*args, **kwargs)
        return wrapper
    return decorator

@accepts_keywords('priority')
def rule(arg=None, **kwargs):
    """Decorator for marking rule classes."""

    def decorator(rule_class):
        required_args = {}
        signature = inspect.signature(rule_class.when)
        for name, arg in signature.parameters.items():
            if name != 'context' and arg.annotation != RuleEngine.Context:
                required_args[name] = arg.annotation if arg.annotation is not inspect.Parameter.empty else Any
        
        def has_required_arguments(context: RuleEngine.Context) -> bool:
            for arg_name, arg_type in required_args.items():
                has_not_allowed_arg = arg_type is None and context.has_attribute(arg_name)
                has_missing_arg = arg_type is not None and not context.has_attribute(arg_name)
                has_wrong_arg_type = arg_type is not Any and context.has_attribute(arg_name) \
                                     and not isinstance(context.get(arg_name), arg_type)

                if has_not_allowed_arg or has_missing_arg or has_wrong_arg_type:
                    return False
            return True
    
        def has_argument_changed(changed_args: list[str]) -> bool:
            return any([arg in changed_args for arg in required_args])

        rule_class.has_argument_changed = has_argument_changed
        rule_class.has_required_arguments = has_required_arguments
        rule_class.required_args = required_args
        rule_class.priority = kwargs.get('priority', 0)
        RuleEngine.register_rule(rule_class)
        return rule_class

    # Returning the correct value depending on whether 
    # the decorator is used as @rule or @rule(...) 
    return decorator(arg) if inspect.isclass(arg) else decorator
