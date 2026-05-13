import asyncio
from open_notebook.database.connection import init_db
from open_notebook.domain.notebook import Source, Asset

async def create_test_sources():
    await init_db()
    
    # Import needed components after DB init to ensure models are ready
    from api.command_service import CommandService
    from commands.source_commands import SourceProcessingInput
    from open_notebook.database.repository import ensure_record_id
    
    for i in range(10):
        # Create a source
        source = Source(
            title=f"Test Async Source {i+1}",
            topics=["test", "async"],
        )
        await source.save()
        
        # Link to notebook
        await source.add_to_notebook("notebook:h1nchslgac1pcad05fzm")
        
        # Submit async command
        command_input = SourceProcessingInput(
            source_id=str(source.id),
            content_state={"content": f"This is test content {i+1} for async graph processing. Testing version 1.85 updates."},
            notebook_ids=["notebook:h1nchslgac1pcad05fzm"],
            transformations=[],
            embed=False,
        )
        
        command_id = await CommandService.submit_command_job(
            "open_notebook",
            "process_source",
            command_input.model_dump()
        )
        
        # Update source with command reference
        source.command = ensure_record_id(command_id)
        await source.save()
        
        print(f"Created source {source.id} with command {command_id}")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(create_test_sources())
