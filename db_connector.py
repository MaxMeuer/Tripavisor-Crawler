import psycopg2
class db_connector:
    def write_into_db_with_return(sql,values):
        conn = None
        try:
            connection = psycopg2.connect(user = "postgres",
                                          password = "2909",
                                          host = "127.0.0.1",
                                          port = "5432",
                                          database = "postgres")

            cursor = connection.cursor()


            # Print PostgreSQL version
            cursor.execute(sql,values)
            connection.commit()
            # get id of entry
            # print('Print: ' + cursor.fetchone()[0])

            id = cursor.fetchone()[0]

        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection.
                if(connection is not None):
                    cursor.close()
                    connection.close()
                    # print("PostgreSQL connection is closed")
        return id


    def write_into_db(sql,values):
        conn = None
        try:
            connection = psycopg2.connect(user = "postgres",
                                          password = "2909",
                                          host = "127.0.0.1",
                                          port = "5432",
                                          database = "postgres")

            cursor = connection.cursor()


            # Print PostgreSQL version
            cursor.execute(sql,values)
            connection.commit()
            # get id of entry
            # print('Print: ' + cursor.fetchone()[0])


        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)
        finally:
            #closing database connection.
                if(connection is not None):
                    cursor.close()
                    connection.close()
                    # print("PostgreSQL connection is closed")




    def write_city(name, coordinates):
        sql = "INSERT INTO city(city_name, coordinates ) VALUES (%s,point%s) RETURNING id"
        city_id = db_connector.write_into_db_with_return(sql, (name, coordinates))
        return city_id


    def write_activity(city_id,name,type):
         sql = "INSERT INTO activity(city_id, type, name ) VALUES (%s,%s,%s) RETURNING id"
         act_id = db_connector.write_into_db_with_return(sql,(city_id,type,name))
         return act_id

    def write_sentiment(act_id,data):
         sql = "INSERT INTO sentiment(activity_id, stars, title,  create_date ) VALUES (%s,%s,%s,%s)"
         print(data[1],data[3])
         db_connector.write_into_db(sql, (act_id,data[0],data[1],data[3]))


# write_into_db( "INSERT INTO city(city_name, coordinates ) VALUES (%s,point%s) RETURNING id",('bsa',(1,2)))
