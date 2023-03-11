CREATE TABLE parents AS
  SELECT "abraham" AS parent, "barack" AS child UNION
  SELECT "abraham"          , "clinton"         UNION
  SELECT "delano"           , "herbert"         UNION
  SELECT "fillmore"         , "abraham"         UNION
  SELECT "fillmore"         , "delano"          UNION
  SELECT "fillmore"         , "grover"          UNION
  SELECT "eisenhower"       , "fillmore";

CREATE TABLE dogs AS
  SELECT "abraham" AS name, "long" AS fur, 26 AS height UNION
  SELECT "barack"         , "short"      , 52           UNION
  SELECT "clinton"        , "long"       , 47           UNION
  SELECT "delano"         , "long"       , 46           UNION
  SELECT "eisenhower"     , "short"      , 35           UNION
  SELECT "fillmore"       , "curly"      , 32           UNION
  SELECT "grover"         , "short"      , 28           UNION
  SELECT "herbert"        , "curly"      , 31;

CREATE TABLE sizes AS
  SELECT "toy" AS size, 24 AS min, 28 AS max UNION
  SELECT "mini"       , 28       , 35        UNION
  SELECT "medium"     , 35       , 45        UNION
  SELECT "standard"   , 45       , 60;


-- The size of each dog
CREATE TABLE size_of_dogs AS
  SELECT name, size FROM dogs, sizes WHERE height > min and height <= max;


-- All dogs with parents ordered by decreasing height of their parent
CREATE TABLE by_parent_height AS
  SELECT child as name FROM dogs, parents WHERE parent = name ORDER BY -height;


-- Filling out this helper table is optional
CREATE TABLE siblings AS
  SELECT a.child AS first, b.child AS second FROM parents AS a, parents AS b WHERE a.parent = b.parent and a.child < b.child;

-- Sentences about siblings that are the same size
CREATE TABLE sentences AS
  SELECT first || " and " || second || " are " || a.size || " siblings" FROM siblings, size_of_dogs AS a, size_of_dogs AS b WHERE first = a.name and second = b.name and a.size = b.size;


-- Ways to stack 4 dogs to a height of at least 170, ordered by total height
CREATE TABLE stacks_helper(dogs, stack_height, last_height, n);

-- Add your INSERT INTOs here
INSERT INTO stacks_helper SELECT name AS dogs, height as stack_height, height as last_height, 1 as n FROM dogs;
INSERT INTO stacks_helper SELECT dogs || ", " || name, stack_height + height, height, n + 1 FROM stacks_helper, dogs WHERE n = 1 AND height > last_height;
INSERT INTO stacks_helper SELECT dogs || ", " || name, stack_height + height, height, n + 1 FROM stacks_helper, dogs WHERE n = 2 AND height > last_height;
INSERT INTO stacks_helper SELECT dogs || ", " || name, stack_height + height, height, n + 1 FROM stacks_helper, dogs WHERE n = 3 AND height > last_height;


CREATE TABLE stacks AS
  SELECT dogs, stack_height AS height FROM stacks_helper WHERE stack_height >= 170 and n = 4 ORDER BY height;

