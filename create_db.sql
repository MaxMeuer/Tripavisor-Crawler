CREATE TABLE city (
  id Serial Primary Key,
  city_name varchar,
  coordinates point
);

Create Table  activity(
  id Serial Primary Key,
  city_id Integer References city(id)  On Delete Cascade,
  type varchar,
  name varchar
);

Create Table sentiment(
  id Serial Primary Key,
  activity_id Integer References activity(id) On Delete Cascade,
  stars Integer,
  title varchar,
  create_date date,
  visit_date date
);

Create Table airport(
	id Serial Primary Key,
	city_id Integer references city(id) On Delete Cascade ,
	name varchar Not Null,
	coordiantes point
);

create Table metadata (
	airport_id integer references airport(id) on Delete Cascade ,
	date date Not Null,
	landings integer,
	departures integer,
	international_landings integer,
	international_departures integer,
	Lufthansa boolean,
	number_of_airlines integer

);

Create Table passengers (
	airport_id integer references airport(id),
	date date,
	departed_international integer,
	enparted_international integer,
	enparted integer ,
	departed integer
);

Create Table airlines (
	id Serial Primary Key,
	airport_id integer references airport(id) On Delete cascade ,
	name varchar
)
