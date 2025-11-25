import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# Load API keys
load_dotenv()

class Lola:
    def __init__(self):
        # --- INITIALIZATION ---
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.gemini = genai.GenerativeModel('gemini-2.5-flash')
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # --- THE MEMORY BOXES ---
        self.short_term_memory = [] 
        
        # [FIX]: Load Long Term Memory from file on startup
        self.memory_file = "chat_history.txt"
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                self.long_term_memory = f.read()
            print(">> [System] Long-term memory loaded from disk.")
        except FileNotFoundError:
            self.long_term_memory = "" # Start fresh if no file exists
            print(">> [System] No memory file found. Starting fresh.")

    def ask_gemini(self, prompt):
        try:
            return self.gemini.generate_content(prompt).text
        except Exception as e:
            print(f"!!! GEMINI CRASHED: {e}") # <--- This prints the real reason
            return f"Gemini Error: {e}"

    def ask_llama(self, prompt):
        try:
            return self.groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            ).choices[0].message.content
        except: return "Groq Error"

    def manage_memory(self):
        """
        Implements the Diamond Decision & File Saving
        """
        # [FIX]: I changed 30 to 6 so you can actually see it work during testing. 
        # If it's 30, you'll be typing all day before it saves!
        if len(self.short_term_memory) > 15: 
            print("   [Memory Full] Summarizing oldest chats...")
            
            # 1. Slice the oldest 2
            oldest_two = "\n".join(self.short_term_memory[:2])
            
            # 2. Update Short Term
            self.short_term_memory = self.short_term_memory[2:]
            
            # 3. Create Summary (Gemini)
            summary_prompt = f"""
            Current Long Term Memory: {self.long_term_memory}
            New Info to Add: {oldest_two}
            
            Task: Merge the New Info into the Memory. Keep it concise.
            """
            new_summary = self.ask_gemini(summary_prompt)
            
            # 4. Update the Variable
            self.long_term_memory = new_summary

            # [FIX]: Save to file immediately
            try:
                with open(self.memory_file, "w", encoding="utf-8") as file:
                    file.write(self.long_term_memory)
                print("   [System] Memory saved to chat_history.txt")
            except Exception as e:
                print(f"   [Error] Could not save memory: {e}")
            
        else:
            pass 

    def run_cycle(self, user_query):
        # 1. BUILD CONTEXT
        context_payload = f"""
        [LONG TERM MEMORY]:
        {self.long_term_memory}
        
        [SHORT TERM CACHE]:
        {chr(10).join(self.short_term_memory)}
        
        [USER QUESTION]:
        {user_query}
        """
        
        # 2. GEMINI RESEARCH
        print(">> Gemini is researching...") # Optional: Comment out to reduce noise
        research_notes = self.ask_gemini(context_payload)
        
        # 3. GROQ ARCHITECTURE
        print(">> Groq is thinking...") # Optional: Comment out to reduce noise
        final_prompt = f"""
        Research Notes: {research_notes}
        User Query: {user_query}
        
        Task: Answer the user's question using the research notes.
        """
        final_output = self.ask_llama(final_prompt)
        
        # 4. UPDATE LISTS
        self.short_term_memory.append(f"User: {user_query}")
        self.short_term_memory.append(f"AI: {final_output}")
        
        # 5. CHECK MEMORY
        self.manage_memory()
        
        return final_output

# --- EXECUTION ---
if __name__ == "__main__":
    ai = Lola()
    print("System Online. (Type 'quit' to exit)")
    
    while True:
        q = input("\nUser: ")
        if q.lower() == "quit": break
        
        response = ai.run_cycle(q)
        print(f"AI: {response}")