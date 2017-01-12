# lacquer

lacquer is a python port of Presto's SQL Parser.

Currently, it doesn't support all the same features as Presto's parser,
but it can parse most SELECT queries and produce the python-equivalent
syntax tree, as well as write the tree back out to SQL.

It was written for [LSST](http://lsst.org) to support the Astronomical 
Data Query Language, "lacquer" which is roughly equivalent to SQL-92.

  

## Known issues
In the porting, the grammar was ported from LL (ANTLRv4) to LALR (PLY).
There's a few shift/reduce errors, but most queries parse just fine.

Queries under test/queries.sql that are commented out don't parse, e.g.:

```sql
select 1 from foo where bar in ((select 1 from baz), 2)
```

### License
This work is licensed under Apache 2.0, the same as Presto.

