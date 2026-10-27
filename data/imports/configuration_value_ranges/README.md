# Configuration value range imports

Each JSON file in this directory is a versioned, declarative
`configuration_attribute_value_ranges` specification. Specifications append
source-backed numeric ranges to
`data/master/configuration_attribute_value_ranges.csv` through:

```text
python tools/dkb.py import-configuration-value-ranges --spec PATH --apply
```

A range specification must preserve both endpoints, endpoint inclusivity,
configuration and optional fuel context, observation date, source registration,
source page, section and exact source text. Scalar values remain in
`configuration_attribute_values.csv` and must not duplicate the same semantic
key on the same date.
