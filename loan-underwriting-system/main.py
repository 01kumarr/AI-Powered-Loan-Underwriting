from loanunderwriting import LoanUnderwritingSystem
import asyncio
import os

async def main():
    """Main entry point"""
    system = LoanUnderwritingSystem()
    
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Check if data files exist
        data_files = ["gst.json", "itr.json", "bank_statement.json"]
        missing_files = []
        for file in data_files:
            if not os.path.exists(os.path.join("data", file)):
                missing_files.append(file)
        
        if missing_files:
            print(f"⚠️  Warning: Missing data files in 'data' directory: {', '.join(missing_files)}")
            print("   Please add these JSON files to the data directory for full functionality.")
        
        # Start the system
        await system.start_system()
        
        # Run interactive session
        await system.run_interactive_session()
        
    finally:
        # Clean up
        system.stop_system()

if __name__ == "__main__":
    asyncio.run(main())