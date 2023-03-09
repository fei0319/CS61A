.read data.sql


CREATE TABLE bluedog AS
  SELECT color, pet from students where color = 'blue' and pet = 'dog';

CREATE TABLE bluedog_songs AS
  SELECT color, pet, song from students where color = 'blue' and pet = 'dog';


CREATE TABLE matchmaker AS
  SELECT a.pet, a.song, a.color, b.color from students as a, students as b where a.time < b.time and a.pet = b.pet and a.song = b.song;


CREATE TABLE sevens AS
  SELECT seven from students, numbers where students.time = numbers.time and students.number = 7 and numbers."7" = "True";


CREATE TABLE favpets AS
  SELECT pet, count(*) from students group by pet order by -count(*) limit 10;


CREATE TABLE dog AS
  SELECT pet, count(*) from students group by pet having pet = "dog";


CREATE TABLE bluedog_agg AS
  SELECT song, count(*) from bluedog_songs group by song order by -count(*);


CREATE TABLE instructor_obedience AS
  SELECT seven, instructor, count(*) from students where seven = "7" group by instructor;

