.PHONY: help dev test test-report clean install docker-up docker-down

# Default target
help:
	@echo "Scene Analyzer - Make Targets"
	@echo "=============================="
	@echo "  make install       - Install dependencies (backend + frontend)"
	@echo "  make dev           - Start development servers"
	@echo "  make test          - Run tests (backend + frontend)"
	@echo "  make test-report   - Run tests with reporting (llm-rule konform)"
	@echo "  make docker-up     - Start Docker Compose stack"
	@echo "  make docker-down   - Stop Docker Compose stack"
	@echo "  make clean         - Clean build artifacts"

# Install dependencies
install:
	@echo "📦 Installing Backend dependencies..."
	cd backend && poetry install
	@echo "📦 Installing Frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Installation complete!"

# Start development servers
dev:
	@echo "🚀 Starting development servers..."
	docker-compose up backend frontend

# Run tests (simple)
test:
	@echo "🧪 Running Backend tests..."
	cd backend && poetry run pytest
	@echo "🧪 Running Frontend tests..."
	cd frontend && npm test

# Run tests with llm-rule v4.1 konformer Reporting
test-report:
	@echo "🧪 Running tests with reporting..."
	@TS=$$(date +%Y%m%d-%H%M); \
	TEST_REPORT_DIR=89_output/test_reports/$$TS; \
	export TEST_REPORT_DIR; \
	mkdir -p "$$TEST_REPORT_DIR"; \
	echo "📊 Test Report Directory: $$TEST_REPORT_DIR"; \
	\
	echo "🐍 Running Backend tests..."; \
	cd backend && poetry run pytest \
		--junitxml="../$$TEST_REPORT_DIR/junit-backend.xml" \
		--cov=app \
		--cov-report=xml:../$$TEST_REPORT_DIR/coverage-backend.xml \
		--cov-report=term-missing \
		|| true; \
	\
	echo "⚛️  Running Frontend tests..."; \
	cd frontend && npm run test:coverage -- \
		--reporter=junit \
		--outputFile=../$$TEST_REPORT_DIR/junit-frontend.xml \
		|| true; \
	\
	rm -f 89_output/test_reports/latest && \
	ln -sfn "$$TS" 89_output/test_reports/latest || true; \
	\
	echo "✅ Test artifacts: $$TEST_REPORT_DIR"; \
	echo "📝 Update 90_reports/ manually or run make reports-update"

# Update reports (manual step after test-report)
reports-update:
	@echo "📝 Updating 90_reports/..."
	@echo "TODO: Implement report generation script"
	@echo "Manually update:"
	@echo "  - 90_reports/test-report.md"
	@echo "  - 90_reports/coverage.md"
	@echo "  - 90_reports/changes.md"

# Docker management
docker-up:
	@echo "🐳 Starting Docker Compose stack..."
	docker-compose up -d
	@echo "✅ Stack started!"
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:4321"
	@echo "API Docs: http://localhost:8000/api/docs"

docker-down:
	@echo "🐳 Stopping Docker Compose stack..."
	docker-compose down
	@echo "✅ Stack stopped!"

docker-logs:
	docker-compose logs -f

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete!"
