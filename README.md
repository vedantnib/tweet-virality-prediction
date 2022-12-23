1. Set up Environment
      - Download logstash, kibana, elastic search, kafka and zookeeper
      - You will need jupyter to run the Spark code. 
      
      - Go to https://www.anaconda.com/ and download anaconda and install it.
            - Once you are set with Anaconda, try to check if anaconda works by typing jupyter in command line.
            -If jupyter is set up properly, terminal will tell you to add commands in addition to jupyter to get the required functionality. 
      
      -Next step is to set up jupyter environment.
            -Write "jupyter notebook" on the same terminal where you executed "jupyter" command earlier.
            - A webpage will popup and you will see directories. That is basically your desktop.
            -On the page you will see two buttons named "New" and "Upload" at the top.
            -Click on the "New" button. It will display a dropdown. Click on the "Terminal" button which will open up a terminal for you.
            -On the Terminal, enter your project folder which consists of the pyspark file that we are running.
      
      -After you enter the folder, run the following commands:

         -> conda install openjdk
         -> conda install pyspark
         -> conda install -c conda-forge findspark

      -To validate pyspark installation, run "pyspark"
      -If everything was set up well, you will enter the pyspark shell.
      -You can exit it by typing "exit()" and press Enter.
      -Now we have basically set up everything required for the project.
      -In your local environment, open the python file called "twitter_credentials.py" and enter your
         twitter api credentials like apiKey, secretKey, bearerToken,etc in 
         the python script where the credential variables are declared.
      
      -Now go back to the jupyter notebook terminal that you started earlier.
      -Enter your project folder from the terminal where the python file is located.
      -You are now ready to run the script. 
               
2. Run the project
      - Open a new terminal in zookeeper folder
      - Start zookeeper by running the below command : 
         -> "bin/zkServer.sh start" and keep the terminal open.
      - Open a new terminal in the Kafka folder.
      - Run the command:
         -> "bin/kafka-server-start.sh config/server.properties" to start kafka
      - Open a new terminal and Create a kafka topic named "abc" to create a kafka topic.
         -> Run "bin/kafka-topics.sh --create --topic abc --bootstrap-server localhost:9092" 
      - Make sure you refer to the configuration files in the project folder and make changes according to the configuration files for logstash, elasticsearch and kibana in your ELK folders, or else logstash will not connect with Elasticsearch and will give error before running Elasticsearch, Kibana and Logstash..
      - Open a new terminal in the Elasticsearch folder.
      - Run the following command:
         -> "bin/elasticsearch" to run elasticsearch.
      - Open a new terminal in the kibana folder.
      - Run the following command:
         ->"bin/kibana" to run kibana
      - Redirect to localhost:5601 and configure kibana. 
      - Open a new terminal from kibana folder and run:
         -> "bin/elasticsearch-create-enrollment-token --scope kibana"
      - Copy paste the token on the configure page of localhost:5601
      - It will then ask you to login.
      - To get the password, open the terminal from elasticsearch folder and run "bin/elasticsearch-reset-password -u elastic", username: elastic and the new password is what you get after running the rest password command.
      - Save the credentials somewhere.
      - Enter the credentials to log into kibana. 
      - Now, go to the logstash folder and run "bin/logstash -f config/logstash-kafka.conf"
      - This will fire up logstash and make it ready for use.
      - From the Jupyter Notebook terminal, Run "spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.1 knn_MapReduce.py"

3. Visualize results
      - After running the python file from the jupyter terminal, go to your kibana dashboard(localhost:5601).
      - On the left, you will find a hamburger icon, click on it and select "Stack Management" under "Management".
      - On the left menu, go to "Data Views" under "Kibana"
      - Click on "Create data view"
      - Set name as "abc" and index as "tweet" which you should see under indexes on the side and then click "Save data view to Kibana".
      - If you don't see it, there is some problem in setting up the pipeline.
      - Click on the hamburger icon on the left again and select "Discover" under "Analytics"
      - Under the hamburger icon you will see a drop-down with some preselected index.
      - Click on the dropdown and select "tweet"
      - You will see your results on the dashboard.
