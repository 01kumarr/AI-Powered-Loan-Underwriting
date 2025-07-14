import asyncio
import subprocess
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Import required modules
from a2a_protocol import A2AProtocol
from agents.datafetcher import handle_a2a_message as datafetcher_handler, register_a2a as register_datafetcher_a2a
from agents.underwriter import handle_a2a_message as underwriter_handler, register_a2a as register_underwriter_a2a
from interactivelsession import InteractiveLoanSession

load_dotenv()


class LoanUnderwritingSystem:
    def __init__(self):
        self.a2a_protocol = A2AProtocol()
        self.datafetcher_process = None
        self.underwriter_process = None
        self.is_running = False
        self.sessions_history = []
        
    async def start_system(self):
        """Initialize and start the loan underwriting system"""
        print("🚀 Starting AI-Powered Loan Underwriting System...")
        print("=" * 60)
        
        # Check LLM configuration
        llm_provider = os.getenv("LLM_PROVIDER", "gemini")
        print(f"🤖 LLM Provider: {llm_provider}")
        
        if llm_provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
            print("⚠️  Warning: GOOGLE_API_KEY not set in .env file")
        elif llm_provider == "ollama":
            print(f"🔗 Ollama URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
            print(f"📦 Ollama Model: {os.getenv('OLLAMA_MODEL', 'llama2')}")
        
        print("-" * 60)
        
        # Register A2A handlers
        self.a2a_protocol.register_agent("datafetcher", datafetcher_handler)
        self.a2a_protocol.register_agent("underwriter", underwriter_handler)
        
        # Register A2A protocol with agents
        register_datafetcher_a2a(self.a2a_protocol)
        register_underwriter_a2a(self.a2a_protocol)
        
        # Start MCP servers in separate processes
        print("\n📦 Starting MCP Servers...")
        
        # Start DataFetcher MCP server
        self.datafetcher_process = subprocess.Popen(
            [sys.executable, "agents/datafetcher.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ DataFetcher MCP Server started")
        
        # Start Underwriter MCP server
        self.underwriter_process = subprocess.Popen(
            [sys.executable, "agents/underwriter.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Underwriter MCP Server started")
        
        # Give servers time to start
        await asyncio.sleep(2)
        
        self.is_running = True
        print("\n✅ System Ready!")
        print("=" * 60)
    
    def stop_system(self):
        """Stop all MCP servers"""
        print("\n🛑 Stopping MCP Servers...")
        if self.datafetcher_process:
            self.datafetcher_process.terminate()
        if self.underwriter_process:
            self.underwriter_process.terminate()
        self.is_running = False
        print("✅ All servers stopped")
    
    async def process_loan_application(self):
        """Process a new loan application with interactive session"""
        print("\n" + "="*60)
        print("📝 NEW LOAN APPLICATION")
        print("="*60)
        
        try:
            # Collect application details
            print("\nPlease enter the application details:")
            applicant_name = input("Applicant Name: ").strip()
            
            while True:
                try:
                    loan_amount = float(input("Loan Amount (₹): ").replace(",", ""))
                    break
                except ValueError:
                    print("❌ Please enter a valid number")
            
            business_type = input("Business Type: ").strip()
            loan_purpose = input("Loan Purpose: ").strip()
            
            while True:
                try:
                    years_in_business = int(input("Years in Business: "))
                    break
                except ValueError:
                    print("❌ Please enter a valid number")
            
            additional_info = input("Additional Information (optional): ").strip()
            
            # Create application object
            application = {
                "applicant_name": applicant_name,
                "loan_amount": loan_amount,
                "business_type": business_type,
                "loan_purpose": loan_purpose,
                "years_in_business": years_in_business,
                "additional_info": additional_info,
                "timestamp": datetime.now().isoformat()
            }
            
            # Start interactive session
            session = InteractiveLoanSession(self, application)
            decision = await session.start_session()
            
            # Store session in history
            self.sessions_history.append({
                "session_id": session.session_id,
                "application": application,
                "decision": decision,
                "timestamp": datetime.now().isoformat()
            })
            
        except KeyboardInterrupt:
            print("\n❌ Application cancelled")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    async def view_sessions_history(self):
        """View history of all loan sessions"""
        print("\n📊 LOAN SESSIONS HISTORY")
        print("-" * 40)
        
        if not self.sessions_history:
            print("No sessions in history")
            return
        
        for session in self.sessions_history[-10:]:  # Last 10 sessions
            print(f"\n📅 Session: {session['session_id']}")
            print(f"   Applicant: {session['application']['applicant_name']}")
            print(f"   Amount: ₹{session['application']['loan_amount']:,.2f}")
            if session['decision']:
                print(f"   Decision: {session['decision'].get('decision', 'PENDING')}")
            print(f"   Date: {session['timestamp']}")
    
    async def view_available_data(self):
        """View available data files"""
        print("\n📁 CHECKING AVAILABLE DATA")
        print("-" * 40)
        
        response = await self.a2a_protocol.send_message(
            sender="main_viewer",
            receiver="datafetcher",
            action="list_available",
            payload={}
        )
        
        if response["status"] == "success":
            available = response["available_data_types"]
            print(f"\n📂 Available Data Files:")
            for data_type in available:
                print(f"   ✓ {data_type}.json")
        else:
            print(f"❌ Error: {response.get('error', 'Unknown error')}")
    
    async def run_interactive_session(self):
        """Run the main interactive session"""
        print("\n💬 INTERACTIVE LOAN UNDERWRITING SYSTEM")
        print("=" * 60)
        print("Commands:")
        print("  new      - Process new loan application")
        print("  history  - View sessions history")
        print("  data     - View available data files")
        print("  help     - Show this help")
        print("  exit     - Exit the system")
        print("=" * 60)
        
        while self.is_running:
            try:
                command = input("\n[Main]> ").strip().lower()
                
                if command == "exit":
                    confirm = input("Exit system? (y/n): ").lower()
                    if confirm == 'y':
                        break
                elif command == "new":
                    await self.process_loan_application()
                elif command == "history":
                    await self.view_sessions_history()
                elif command == "data":
                    await self.view_available_data()
                elif command == "help":
                    print("\nCommands: new, history, data, help, exit")
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n⚠️  Use 'exit' to quit properly")
                continue
            except Exception as e:
                print(f"❌ Error: {str(e)}")
