CREATE TABLE city (
  id Serial Primary Key,
  city_name varchar,
  coordinates point
);

Create Table  activity(
  id Serial Primary Key,
  city_id Integer References city(id),
  type varchar,
  name varchar
);

Create Table sentiment(
  id Serial Primary Key,
  activity_id Integer References activity(id),
  stars Integer,
  title varchar,
  create_date date,
  visit_date date
)
