include ./backend.Makefile
-include ./local.Makefile

# Load environment variables
include .env
export

define HELP
Usage: make <target>
Example usage:
	make help
	make init
	make run

Available <target>:
	Commonly used:
	init            - Initialize the environment for local development
	run             - Run whole services in 1 command

	Running application:
	build           - Build the application
	up              - Start the application
	down            - Stop the application (with automatic cleanup)
	logs            - Follow the logs

	Cleanup:
	clean           - Clean unused Docker resources
	clean-all       - Clean all Docker resources (including images)
	clean-volumes   - Clean all volumes (WARNING: removes database data)
	restart-clean   - Restart with cleanup

endef
export HELP

help:
	@echo "$$HELP"
	@echo "$$BACKEND_HELP"
	@if [ -n "$$LOCAL_HELP" ]; then echo "$$LOCAL_HELP"; fi

init: backend/init build
run: build up backend/migrate logs

build:
	docker compose build

up:
	docker compose up -d
	@echo "Cleaning up unused Docker resources..."
	docker system prune -f
	docker volume prune -f

down:
	docker compose down

logs:
	docker compose logs -f

check: backend/lint-fix backend/typecheck backend/lint backend/test

test: backend/test

# Docker cleanup commands
clean:
	@echo "Cleaning Docker resources..."
	docker system prune -f
	docker volume prune -f
	@echo "Docker cleanup completed"

clean-all:
	@echo "Cleaning all Docker resources (including images)..."
	docker system prune -a -f
	docker volume prune -f
	@echo "Complete Docker cleanup finished"

clean-volumes:
	@echo "WARNING: This will remove all Docker volumes including database data!"
	@echo "Press Ctrl+C to cancel or wait 5 seconds to continue..."
	@sleep 5
	docker compose down -v
	@echo "All volumes cleaned"

restart-clean: down clean up
	@echo "Server restarted with cleanup"
