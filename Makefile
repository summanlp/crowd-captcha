
build:
	docker build db -t crowdcaptcha-db
	docker build . -t crowdcaptcha-web

run:
	docker run -e POSTGRES_PASSWORD=torrepaswd\
		-e POSTGRES_USER=torre \
		-e POSTGRES_DB=crowdcaptcha \
		-h ccdb crowdcaptcha-db &
	sleep 3
	docker run -p 4001:5000 crowdcaptcha-web &

killall: 
	docker container ls \
	| grep crowdcaptcha | cut -c 1-5 \
	| xargs -I {container_name} \
	  docker container kill {container_name}
