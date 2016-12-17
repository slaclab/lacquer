select 1 from foo where bar in
    (select 1 from baz);

select 1 from foo where bar in
    ((select 1 from baz));

select 1 from foo where bar in (2);

select 1 from foo where bar in (2, (select 1 from baz));

select 1 from foo where bar in ((select 1 from baz), 2);

select 1 from foo where bar in ((select 1 from dual), (select 2 from baz));


select 1 from DUAL where 1=1;

select "!" from dual x;

select r(x, 1, 2, CURRENT_TIME);

(select 1);

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

-- adql
select TOP 10 case when x=1 then y else z END, a
from "II/295/SSTGC","II/293/glimpse"
where 1=CONTAINS(POINT('ICRS',"II/295/SSTGC".RAJ2000,"II/295/SSTGC".DEJ2000),
             BOX('GALACTIC', 0, 0, 30/60., 10/60.))
  AND 1=CONTAINS(POINT('ICRS',"II/295/SSTGC".RAJ2000,"II/295/SSTGC".DEJ2000),
            CIRCLE('ICRS',"II/293/glimpse".RAJ2000,"II/293/glimpse".DEJ2000, 2/3600.0));
