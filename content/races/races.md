male_names: Comma separated list of male names.
female_names: Comma separated list of female names.
family_names: Comma separated list of family names.
size: Movement speed per turn in combat (feet/turn)
subraces: List of subraces.
name: Name of the subrace.
traits: The list of traits for the subrace.


# Traits
## Ability score modifier

This trait type allows to increase/decrease the value of an ability scores.
The mandatory field **modifiers** is a dictionary where the value is added to the ability score. The allowed keys are:
  - strength
  - dexterity
  - constitution
  - intelligence
  - wisdom
  - charisma

```yaml
type: ability_score_modifier
data:
  dexterity: 2
```

## Armor type proficiency

This trait type allows to grant proficiency for the specified armor types.
The mandatory list **armor_types** specifies the armor types. Allowed values are: 
  - light
  - medium
  - heavy
  - shields

```yaml
type: armor_type_proficiency
data:
  armor_types: 
    - heavy
```

## Weapon class proficiency

This trait type allows to grant proficiency for the specified weapon classes. 
The mandatory list **weapon_classes** specifies the weapon classes. Allowed values are:
  - simple
  - martial

```yaml
type: weapon_class_proficiency
data:
  weapon_classes:
    - martial
```

## Weapon proficiency

This trait type allows to grant proficiency for the specified weapons.
The mandatory list **weapons** specifies the weapon types. Allowed values are
the names in **weapons.yaml**.

```yaml
type: weapon_proficiency
data:
  weapons:
    - Spear
    - Mace
```

## Saving throw proficiency

This trait type allows to grant proficiency for the specified saving throws.
The mandatory list **abilities** specifies the abilities for the saving throws.
The allowed values are:
  - strength
  - dexterity
  - constitution
  - intelligence
  - wisdom
  - charisma

```yaml
type: saving_throw_proficiency
data:
  abilities:
    - dexterity
```