CSE586 PROJECT2 Phase3

1.open the terminal, run the following.
2.$cd <the direction of project2 phase 3 which including the docker-compose.yml file>
3.$docker-compose up
4.Docker will build 3 sub/pub system images and 1 mySQL image
5.The three pub/sub systems containers are running on:
	http://0.0.0.0:5000
	http://0.0.0.0:4000
	http://0.0.0.0:2000
6.The sub system is on the page http://0.0.0.0:port/sub, the pub system is on the page http://0.0.0.0:port/pub
7.The three containers will share the information via the mySQL container, thus realize the pub/sub functions
8.Pay more attention to the messages of subscribers, remember to refresh the sub page