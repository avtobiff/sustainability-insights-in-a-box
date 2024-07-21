netsim:
	make -C dev/netsim
	if [ ! -d netsim ]; then                 \
		ncs-netsim create-network dev 1 dev; \
	fi

start-netsim: netsim
	ncs-netsim -a start

stop-netsim:
	ncs-netsim -a stop

clean:
	make -C dev/netsim clean
	rm -rf netsim
