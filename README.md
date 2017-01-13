# lacquer [![Build Status](https://travis-ci.org/slaclab/lacquer.svg?branch=master)](https://travis-ci.org/slaclab/lacquer)

lacquer is a python port of Presto's SQL Parser.

Currently, it doesn't support all the same features as Presto's parser,
but it can parse most SELECT queries and produce the python-equivalent
syntax tree, as well as write the tree back out to SQL.

It was written for [LSST](http://lsst.org) to support the Astronomical 
Data Query Language, which is roughly equivalent to SQL-92.

## Advantages
* Only two dependencies, PLY and future. Runs on Python 2 and 3 (tested on 2.7 and 3.5).
* Uses the Presto AST IR and Visitor patterns
  * Code can easily be ported to lacquer from Python

## Known issues
**Only SELECT statements are currently supported.** This is mostly the case with
Presto as well.

In the porting, the grammar was ported from LL (ANTLRv4) to LALR (PLY).
There's a few shift/reduce errors, but most queries parse just fine, but you 
may run across a few errors, for example:

```sql
select 1 from foo where bar in ((select 1 from baz), 2)
```

### License
This work is licensed under Apache 2.0, the same as Presto.

