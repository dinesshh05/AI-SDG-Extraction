@echo off
:: ==============================================
:: AI SDG EXTRACTOR - restructure script (cmd.exe)
:: ==============================================

:: 1. Create new folders
mkdir retrieval_core extractor chatbot backend\routers frontend\src cache\uploads legacy

:: 2. Straight moves - unchanged files
move /Y src\parser.py extractor\parser.py
move /Y src\chunker.py extractor\chunker.py
move /Y src\filtering.py extractor\filtering.py
move /Y src\query_bank.py extractor\query_bank.py
move /Y src\validator.py extractor\validator.py
move /Y src\excel_writer.py extractor\excel_writer.py
move /Y src\extractor.py extractor\llm_extraction.py

:: 3. Straight moves - files that need a code fix afterward (do the fix by hand)
move /Y src\embeddings.py retrieval_core\embeddings.py
move /Y src\vector_store.py retrieval_core\vector_store.py

:: 4. retrieval.py becomes 3 files - a script can't split code for you.
::    Keep the original as a reference in legacy/, then create 3 stub files to write into.
move /Y src\retrieval.py legacy\retrieval.py.reference
echo # TODO: move shared retrieval logic here from legacy\retrieval.py.reference > retrieval_core\retrieval.py
echo # TODO: move SDG-specific orchestration here from legacy\retrieval.py.reference > extractor\retrieval_orchestration.py
echo # TODO: move SDG keyword lists here from legacy\retrieval.py.reference > extractor\sdg_keywords.py

:: 5. app.py is retired - back it up, then stub the two new router files
move /Y app.py legacy\app.py.bak
echo # TODO: rebuild extraction endpoint here, referencing legacy\app.py.bak > backend\routers\extract.py
echo # TODO: rebuild status endpoint here, referencing legacy\app.py.bak > backend\routers\status.py

:: 6. main.py is retired - back it up, then stub the orchestrator + cli
move /Y main.py legacy\main.py.bak
echo # TODO: rebuild orchestrator here, referencing legacy\main.py.bak > extractor\extractor.py
echo # TODO: rebuild CLI entry point here, referencing legacy\main.py.bak > extractor\cli.py

:: 7. Clean up src/
del src\__init__.py
rmdir /s /q src\__pycache__ 2>nul
rmdir src 2>nul

:: 8. __init__.py for new packages
type nul > retrieval_core\__init__.py
type nul > extractor\__init__.py
type nul > chatbot\__init__.py
type nul > backend\__init__.py
type nul > backend\routers\__init__.py

:: 9. Old cache - schema changed, let it regenerate
del cache\embeddings.db 2>nul

:: 10. output/ -> cache/reports/ (merge contents if output/ exists, then remove it)
if exist output (
    xcopy /E /I /Y output cache\reports\
    rmdir /s /q output
) else (
    mkdir cache\reports
)

echo.
echo ==============================================
echo Mechanical moves done. Still needs manual work:
echo  - extractor\excel_writer.py            : fix output dir derivation
echo  - retrieval_core\embeddings.py / vector_store.py : apply the "shared" + namespace-column changes
echo  - retrieval_core\retrieval.py, extractor\retrieval_orchestration.py, extractor\sdg_keywords.py : split from legacy\retrieval.py.reference
echo  - backend\routers\extract.py, status.py : rebuild from legacy\app.py.bak
echo  - extractor\extractor.py, extractor\cli.py : rebuild from legacy\main.py.bak
echo  - tests\ : update imports (src.chunker -^> extractor.chunker, etc.)
echo  - .env : add new variables from .env.example
echo ==============================================
