from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import json



connection = psycopg2.connect(user = "postgres",
                              password = "Rascal9013123",
                              host = "localhost",
                              port = "5032",
                              database = "Portfolio_Dara_Schema")

cursor = connection.cursor()
cursor.execute('SELECT * FROM "Portfolio_data"."Users"')
records = cursor.fetchall()

cursor.close()
connection.close()

app = Flask(__name__)
CORS(app)

@app.route("/api/data", methods=["GET"])
def get_resources():
    connection = psycopg2.connect(user = "postgres",
                              password = "Rascal9013123",
                              host = "localhost",
                              port = "5032",
                              database = "Portfolio_Dara_Schema")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM "Portfolio_data"."Users"')
    records = cursor.fetchall()
    
    users = []
    for row in records:
      user = {
        'id': row[0],
        'name': row[1],
        'password': row[2]
      }
      users.append(user)
    
    cursor.close()
    connection.close()
    print(jsonify(users))
    return jsonify(users)
  
if __name__ == "__main__":
    app.run()
    
