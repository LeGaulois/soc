#-*- coding: utf-8 -*-
import psycopg2


def testConnectionSQL(host,port,database,user,password):
    try:
        conn = psycopg2.connect(host=host,port=port,database=database,user=user,password=password)
    except Exception as e:
        print str(e)
