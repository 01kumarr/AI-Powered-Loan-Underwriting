import json
from typing import Dict, Any
from datetime import datetime
from server.underwritertool import llm_analyze_application, make_llm_decision
from llm_provider import LLMProvider

# Import required modules

class InteractiveLoanSession:
    """Manages an interactive loan underwriting session"""
    
    def __init__(self, system, application: Dict[str, Any]):
        self.system = system
        self.application = application
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_history = []
        self.fetched_documents = {}
        self.ai_assessments = []
        self.additional_notes = []
        self.current_decision = None
        self.session_active = True
        
    async def start_session(self):
        """Start the interactive underwriting session"""
        print("\n" + "="*60)
        print("🏦 INTERACTIVE LOAN UNDERWRITING SESSION")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        print(f"Applicant: {self.application['applicant_name']}")
        print(f"Amount: ₹{self.application['loan_amount']:,.2f}")
        print("\n💡 Type 'help' for available commands")
        print("="*60)
        
        # Initial AI analysis
        await self.analyze_application()
        
        # Interactive loop
        while self.session_active:
            try:
                command = input("\n[Underwriter]> ").strip().lower()
                
                if command == "exit":
                    confirm = input("Exit session? (y/n): ").lower()
                    if confirm == 'y':
                        self.session_active = False
                elif command == "help":
                    self.show_help()
                elif command == "analyze":
                    await self.analyze_application()
                elif command.startswith("fetch"):
                    await self.fetch_documents(command)
                elif command.startswith("search"):
                    await self.search_information(command)
                elif command.startswith("question"):
                    await self.ask_ai_question(command)
                elif command == "review":
                    await self.review_all_data()
                elif command == "decision":
                    await self.make_decision()
                elif command.startswith("note"):
                    self.add_note(command)
                elif command == "report":
                    await self.generate_report()
                elif command == "export":
                    await self.export_report()
                elif command == "history":
                    self.show_conversation_history()
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n⚠️  Use 'exit' to end the session properly")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print("\n✅ Session ended")
        return self.current_decision
    
    def show_help(self):
        """Show available commands"""
        print("\n📚 AVAILABLE COMMANDS:")
        print("-" * 40)
        print("  analyze              - Re-analyze the application")
        print("  fetch <doc_type>     - Fetch specific document (gst/itr/bank_statement)")
        print("  search <query>       - Search for business/applicant information")
        print("  question <query>     - Ask AI a specific question")
        print("  review               - Review all collected data")
        print("  decision             - Make/update loan decision")
        print("  note <text>          - Add a note to the case")
        print("  report               - Generate comprehensive report")
        print("  export               - Export report to file")
        print("  history              - Show conversation history")
        print("  help                 - Show this help")
        print("  exit                 - Exit the session")
    
    async def analyze_application(self):
        """Analyze the loan application"""
        print("\n🔄 Analyzing application...")        
        llm = LLMProvider()
        
        # Get AI analysis
        app_analysis = await llm_analyze_application(self.application)
        self.ai_assessments.append({
            "timestamp": datetime.now().isoformat(),
            "type": "initial_analysis",
            "content": app_analysis
        })
        
        print("\n🤖 AI ANALYSIS:")
        print("-" * 40)
        print(app_analysis["analysis"])
        print(f"\n📋 Recommended documents: {', '.join(app_analysis['required_documents'])}")
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "analyze",
            "result": app_analysis
        })
        
        # Ask if underwriter wants to fetch recommended documents
        fetch_all = input("\nFetch all recommended documents? (y/n): ").lower()
        if fetch_all == 'y':
            for doc in app_analysis['required_documents']:
                await self.fetch_single_document(doc)
    
    async def fetch_documents(self, command: str):
        """Fetch specific documents"""
        parts = command.split()
        if len(parts) < 2:
            print("Usage: fetch <document_type>")
            print("Available types: gst, itr, bank_statement, all")
            return
        
        doc_type = parts[1]
        if doc_type == "all":
            doc_types = ["gst", "itr", "bank_statement"]
            for dt in doc_types:
                await self.fetch_single_document(dt)
        else:
            await self.fetch_single_document(doc_type)
    
    async def fetch_single_document(self, doc_type: str):
        """Fetch a single document"""
        print(f"\n📂 Fetching {doc_type} data...")
        
        response = await self.system.a2a_protocol.send_message(
            sender="interactive_underwriter",
            receiver="datafetcher",
            action="fetch_and_analyze",
            payload={
                "data_types": [doc_type],
                "analysis_type": "detailed"
            }
        )
        
        if response["status"] == "success":
            self.fetched_documents[doc_type] = {
                "timestamp": datetime.now().isoformat(),
                "data": response["summary"]
            }
            print(f"\n✅ {doc_type.upper()} Data Retrieved:")
            print(response["summary"])
            
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": f"fetch_{doc_type}",
                "result": response["summary"]
            })
        else:
            print(f"❌ Error fetching {doc_type}: {response.get('error')}")
    
    async def search_information(self, command: str):
        """Search for additional information"""
        query = command.replace("search", "").strip()
        if not query:
            query = input("Enter search query: ")
        
        print(f"\n🔍 Searching for: {query}")
        
        response = await self.system.a2a_protocol.send_message(
            sender="interactive_underwriter",
            receiver="datafetcher",
            action="search_business",
            payload={
                "business_name": query,
                "search_type": "comprehensive"
            }
        )
        
        if response["status"] == "success":
            results = response["search_results"]
            print("\n📊 Search Results:")
            for i, result in enumerate(results.get('results', []), 1):
                print(f"\n{i}. {result['title']}")
                print(f"   {result['snippet']}")
            
            if 'ai_summary' in results:
                print(f"\n🤖 AI Summary:")
                print(results['ai_summary'])
            
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "search",
                "query": query,
                "result": results
            })
    
    async def ask_ai_question(self, command: str):
        """Ask AI a specific question about the application"""
        question = command.replace("question", "").strip()
        if not question:
            question = input("Enter your question: ")
        
        llm = LLMProvider()
        
        # Prepare context
        context = f"""
        Application Details:
        {json.dumps(self.application, indent=2)}
        
        Fetched Documents:
        {json.dumps(self.fetched_documents, indent=2)}
        
        Previous Assessments:
        {json.dumps(self.ai_assessments, indent=2)}
        
        Question: {question}
        """
        
        print("\n🤔 Thinking...")
        response = await llm.generate(
            context,
            "You are an expert loan underwriter. Answer the question based on the provided context."
        )
        
        print(f"\n🤖 AI Response:")
        print(response)
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "ai_question",
            "question": question,
            "answer": response
        })
    
    async def review_all_data(self):
        """Review all collected data"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE DATA REVIEW")
        print("="*60)
        
        print("\n1️⃣ APPLICATION DETAILS:")
        print("-" * 40)
        for key, value in self.application.items():
            if key != "timestamp":
                print(f"   {key.replace('_', ' ').title()}: {value}")
        
        print("\n2️⃣ FETCHED DOCUMENTS:")
        print("-" * 40)
        if self.fetched_documents:
            for doc_type, doc_data in self.fetched_documents.items():
                print(f"\n   📄 {doc_type.upper()}:")
                print(f"   Fetched at: {doc_data['timestamp']}")
                print("   " + "-"*20)
                print(doc_data['data'])
        else:
            print("   No documents fetched yet")
        
        print("\n3️⃣ AI ASSESSMENTS:")
        print("-" * 40)
        for assessment in self.ai_assessments:
            print(f"\n   🤖 {assessment['type']} ({assessment['timestamp']})")
            if isinstance(assessment['content'], dict):
                print(f"   Analysis: {assessment['content'].get('analysis', 'N/A')}")
        
        print("\n4️⃣ ADDITIONAL NOTES:")
        print("-" * 40)
        if self.additional_notes:
            for note in self.additional_notes:
                print(f"   • {note['timestamp']}: {note['text']}")
        else:
            print("   No additional notes")
    
    async def make_decision(self):
        """Make or update the loan decision"""
        print("\n🎯 LOAN DECISION")
        print("-" * 40)
        
        # Get all data for decision making
        
        # Compile all fetched data
        all_data = "\n\n".join([
            f"{doc_type.upper()}: {doc_data['data']}" 
            for doc_type, doc_data in self.fetched_documents.items()
        ])
        
        if not all_data:
            print("⚠️  No documents fetched. Fetch required documents first.")
            return
        
        print("\n🤔 AI making decision based on all available data...")
        decision = await make_llm_decision(self.application, all_data)
        
        print(f"\n📌 AI RECOMMENDATION:")
        print(f"   Risk Score: {decision.get('risk_score', 'N/A')}/100")
        print(f"   Decision: {decision.get('decision', 'PENDING')}")
        print(f"   Reasoning: {decision.get('reasoning', 'N/A')}")
        if decision.get('conditions'):
            print(f"   Conditions: {', '.join(decision['conditions'])}")
        
        # Allow manual override
        print("\n📝 Manual Decision Override:")
        override = input("Accept AI decision? (y/n/modify): ").lower()
        
        if override == 'modify':
            decision['decision'] = input("Enter decision (APPROVED/REJECTED/APPROVED_WITH_CONDITIONS): ")
            decision['reasoning'] = input("Enter reasoning: ")
            conditions = input("Enter conditions (comma-separated): ")
            decision['conditions'] = [c.strip() for c in conditions.split(',')] if conditions else []
        
        self.current_decision = decision
        print("\n✅ Decision recorded")
    
    def add_note(self, command: str):
        """Add a note to the case"""
        note_text = command.replace("note", "").strip()
        if not note_text:
            note_text = input("Enter note: ")
        
        self.additional_notes.append({
            "timestamp": datetime.now().isoformat(),
            "text": note_text
        })
        print("✅ Note added")
    
    async def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE LOAN UNDERWRITING REPORT")
        print("="*60)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Session ID: {self.session_id}")
        print("="*60)
        
        # Executive Summary
        print("\n📊 EXECUTIVE SUMMARY")
        print("-" * 40)
        print(f"Applicant: {self.application['applicant_name']}")
        print(f"Loan Amount: ₹{self.application['loan_amount']:,.2f}")
        print(f"Business Type: {self.application['business_type']}")
        print(f"Purpose: {self.application['loan_purpose']}")
        
        if self.current_decision:
            print(f"\nFinal Decision: {self.current_decision['decision']}")
            print(f"Risk Score: {self.current_decision.get('risk_score', 'N/A')}/100")
        else:
            print("\nFinal Decision: PENDING")
        
        # Detailed Analysis
        print("\n📈 DETAILED ANALYSIS")
        print("-" * 40)
        
        # AI Assessments
        print("\n1. AI Assessments:")
        for i, assessment in enumerate(self.ai_assessments, 1):
            print(f"\n   Assessment {i} ({assessment['timestamp']}):")
            if isinstance(assessment['content'], dict):
                print(f"   {assessment['content'].get('analysis', 'N/A')}")
        
        # Financial Documents Summary
        print("\n2. Financial Documents Analysis:")
        if self.fetched_documents:
            for doc_type, doc_data in self.fetched_documents.items():
                print(f"\n   {doc_type.upper()}:")
                print(f"   {doc_data['data'][:500]}...")  # First 500 chars
        else:
            print("   No documents analyzed")
        
        # Decision Rationale
        if self.current_decision:
            print("\n3. Decision Rationale:")
            print(f"   {self.current_decision.get('reasoning', 'No reasoning provided')}")
            if self.current_decision.get('conditions'):
                print("\n4. Conditions:")
                for condition in self.current_decision['conditions']:
                    print(f"   • {condition}")
        
        # Additional Notes
        if self.additional_notes:
            print("\n5. Underwriter Notes:")
            for note in self.additional_notes:
                print(f"   • {note['timestamp']}: {note['text']}")
        
        # Risk Factors
        print("\n6. Key Risk Factors:")
        print("   • Debt-to-Income Ratio")
        print("   • Business Stability")
        print("   • Tax Compliance")
        print("   • Credit History")
        
        print("\n" + "="*60)
        print("END OF REPORT")
        print("="*60)
    
    async def export_report(self):
        """Export report to file"""
        filename = f"loan_report_{self.application['applicant_name'].replace(' ', '_')}_{self.session_id}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Redirect print to file
                import sys
                original_stdout = sys.stdout
                sys.stdout = f
                
                await self.generate_report()
                
                # Restore stdout
                sys.stdout = original_stdout
            
            print(f"\n✅ Report exported to: {filename}")
            
            # Also save as JSON for data processing
            json_filename = filename.replace('.txt', '.json')
            report_data = {
                "session_id": self.session_id,
                "application": self.application,
                "fetched_documents": self.fetched_documents,
                "ai_assessments": self.ai_assessments,
                "additional_notes": self.additional_notes,
                "current_decision": self.current_decision,
                "conversation_history": self.conversation_history
            }
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"✅ Data exported to: {json_filename}")
            
        except Exception as e:
            print(f"❌ Error exporting report: {str(e)}")
    
    def show_conversation_history(self):
        """Show conversation history"""
        print("\n📜 CONVERSATION HISTORY")
        print("-" * 40)
        
        if not self.conversation_history:
            print("No conversation history yet")
            return
        
        for entry in self.conversation_history[-10:]:  # Last 10 entries
            print(f"\n📅 {entry['timestamp']}")
            print(f"   Action: {entry['action']}")
            if 'query' in entry:
                print(f"   Query: {entry['query']}")
            if 'question' in entry:
                print(f"   Question: {entry['question']}")

