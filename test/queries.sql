select 1 from foo where bar in (select 1 from baz);

select 1 from foo where bar in ((select 1 from baz));

select 1 from foo where bar in (2);

select 1 from foo where bar in (2, (select 1 from baz));

-- FIXME: Broken
--select 1 from foo where bar in ((select 1 from baz), 2);

-- FIXME: Broken
--select 1 from foo where bar in ((select 1 from dual), (select 2 from baz));

-- FIXME: This probably shouldn't work
(select 1);

select a from (select a, b from foo) as bar;

select a from (select a, b from foo) as bar where bar.b in (select b from baz);

select 1 from DUAL where 1=1;

select "!" from dual x;

select r(x, 1, 2, CURRENT_TIME);
select cast(a as varchar(2)), b from foo;

select foo() from bar;
select count(*) from foo;

select y.b from ( select 1 as b from foo as a) y;
select a.b.c.d from foo;
select 1 from foo;
select 1, 2;
select true;
select null;
select hi;
select 'hi';
select 1, 2;
select 1 a from foo;
select 1 as a from foo;
select 1 from foo a;
select 1 from foo as a;
select a.bar from foo a;
select 1 from foo a where a.bar = 3 or z.bax = 4;
select `foo`;

select a, b from foo order by a;
select a, b from foo order by a, b;
select fun(a), b from foo order by fun(a), b;
select a, b from foo where 1=1 order by a, b;
select foo.a as foo_a, bar.b as bar_b, c from foo, y bar order by foo_a, bar_b;

select foo, bar from baz group by foo order by baz;

select
	l_returnflag,
	l_linestatus,
	sum(l_quantity) as sum_qty,
	sum(l_extendedprice) as sum_base_price,
	sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
	sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
	avg(l_quantity) as avg_qty,
	avg(l_extendedprice) as avg_price,
	avg(l_discount) as avg_disc
from
	lineitem
where
	l_shipdate <= 1234
group by
	l_returnflag,
	l_linestatus
order by
	l_returnflag,
	l_linestatus;


select TOP 10 case when x=1 then y else z END, a
from "II/295/SSTGC","II/293/glimpse"
where 1=CONTAINS(POINT('ICRS',"II/295/SSTGC".RAJ2000,"II/295/SSTGC".DEJ2000),
             BOX('GALACTIC', 0, 0, 30/60., 10/60.))
  AND 1=CONTAINS(POINT('ICRS',"II/295/SSTGC".RAJ2000,"II/295/SSTGC".DEJ2000),
            CIRCLE('ICRS',"II/293/glimpse".RAJ2000,"II/293/glimpse".DEJ2000, 2/3600.0));
