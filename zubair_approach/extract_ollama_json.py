"""
FAQ Extraction Script using Ollama (JSON Version)
==================================================
This script extracts Frequently Asked Questions (FAQs) from email replies
using Ollama's qwen2.5:14b-instruct-q4_K_M model.

The script:
1. Loads email data from a JSON file
2. Extracts Zubair's replies
3. Uses map-reduce summarization to extract FAQs
4. Saves the results to a CSV file
"""

import csv
import json
import os
import sys
import warnings
from tqdm import tqdm
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.summarize import load_summarize_chain

# Suppress deprecation warnings and token length warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*Token indices sequence length.*")


def load_json(file_path):
    """
    Load email data from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        list: List of dictionaries containing email data
    """
    print(f"\n{'='*60}")
    print(f"📂 LOADING JSON FILE: {file_path}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File '{file_path}' not found!")
        sys.exit(1)
    
    try:
        print(f"🔄 Loading JSON file...")
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data_list = json.load(json_file)
        
        if not isinstance(data_list, list):
            print(f"❌ ERROR: JSON file must contain a list/array of email objects!")
            sys.exit(1)
        
        total_entries = len(data_list)
        if total_entries > 0:
            print(f"✅ Found {total_entries} email entries in JSON file\n")
            
            # Validate structure
            valid_entries = 0
            for entry in tqdm(data_list, desc="Validating entries", unit=" emails", ncols=80):
                if isinstance(entry, dict) and "reply" in entry:
                    valid_entries += 1
            
            print(f"\n✅ Successfully loaded {valid_entries} valid email entries\n")
            return data_list
        else:
            print(f"⚠️  File appears empty\n")
            return []
            
    except json.JSONDecodeError as e:
        print(f"❌ ERROR parsing JSON: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR loading JSON file: {str(e)}")
        sys.exit(1)


def extract_faq(text_data):
    """
    Extract FAQs from email text using map-reduce summarization.
    
    Args:
        text_data (str): Combined text of all email replies
        
    Returns:
        list: List of FAQ dictionaries with question and answer
    """
    print(f"\n{'='*60}")
    print(f"🤖 INITIALIZING OLLAMA MODEL")
    print(f"{'='*60}\n")
    
    # Initialize Ollama Chat Model with qwen2.5:14b-instruct-q4_K_M model
    print("🔄 Connecting to Ollama...")
    print("   Model: qwen2.5:14b-instruct-q4_K_M")
    print("   Temperature: 0 (for consistent results)\n")
    
    try:
        llm = ChatOllama(
            model="qwen2.5:14b-instruct-q4_K_M",
            temperature=0,
            verbose=False
        )
        print("✅ Ollama model initialized successfully\n")
    except Exception as e:
        print(f"❌ ERROR initializing Ollama: {str(e)}")
        print("   Make sure Ollama is running and the model is downloaded!")
        sys.exit(1)
    
    print(f"{'='*60}")
    print(f"📝 SPLITTING TEXT INTO CHUNKS")
    print(f"{'='*60}\n")
    
    # Split text into manageable chunks for processing
    # Reduced chunk size to fit model's 1024 token limit
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # Reduced from 3000 to fit model's 1024 token limit
        chunk_overlap=50,     # Increased overlap for better context preservation
        length_function=len,
        is_separator_regex=False
    )
    
    print(f"📊 Original text length: {len(text_data):,} characters")
    texts = text_splitter.split_text(text_data)
    docs = text_splitter.create_documents(texts)
    
    print(f"✅ Split into {len(docs)} chunks for processing\n")
    
    # Define the map prompt for extracting FAQs from each chunk
    # Improved: More specific about what to extract, mentions context clues
    map_prompt = """
    EMAIL REPLIES FROM ZUBAIR (a graduate student):
    {text}
    ----
    
    Extract recurring questions and answers about Zubair from these email replies. 
    Focus on: availability/preferences, important links, contact info, work samples, background info.
    Return JSON array: [{{"question": "...", "answer": "..."}}]
    """
    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])
    
    # Define the combine prompt for merging all extracted FAQs
    # Improved: More specific about deduplication and consolidation
    combine_prompt = """
    EXTRACTED FAQs ABOUT ZUBAIR:
    {text}
    ----
    
    Consolidate into final FAQ list: merge duplicates, keep unique questions with clear answers.
    Return JSON array: [{{"question": "...", "answer": "..."}}]
    """
    combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])
    
    print(f"{'='*60}")
    print(f"🔄 RUNNING MAP-REDUCE SUMMARIZATION")
    print(f"{'='*60}\n")
    print("📋 Processing chunks (this may take a while)...")
    print("   Progress will be shown below\n")
    
    # Create and run the summarization chain
    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=combine_prompt_template,
        verbose=False  # Suppress verbose output
    )
    
    try:
        # Show progress
        print(f"📊 Processing {len(docs)} chunks...")
        with tqdm(total=len(docs), desc="Processing chunks", unit=" chunk", ncols=80) as pbar:
            # Run the chain (we'll update progress manually)
            output = summary_chain.run(docs)
            pbar.update(len(docs))
        print(f"✅ Summarization complete!\n")
        
        # Parse the JSON output
        print(f"{'='*60}")
        print(f"📦 PARSING RESULTS")
        print(f"{'='*60}\n")
        
        # Try to extract JSON from the output (it might have extra text)
        output_clean = output.strip()
        
        # If output doesn't start with '[', try to find JSON array
        if not output_clean.startswith('['):
            # Try to find JSON array in the output
            start_idx = output_clean.find('[')
            end_idx = output_clean.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                output_clean = output_clean[start_idx:end_idx]
        
        faqs = json.loads(output_clean)
        print(f"✅ Successfully extracted {len(faqs)} FAQs\n")
        
        return faqs
        
    except json.JSONDecodeError as e:
        print(f"❌ ERROR parsing JSON output: {str(e)}")
        print(f"\n📄 Raw output received:\n{output[:500]}...\n")
        print("⚠️  Attempting to fix JSON format...")
        
        # Try to fix common JSON issues
        try:
            # Remove markdown code blocks if present
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0]
            elif "```" in output:
                output = output.split("```")[1].split("```")[0]
            
            output = output.strip()
            faqs = json.loads(output)
            print(f"✅ Successfully parsed {len(faqs)} FAQs after fixing format\n")
            return faqs
        except:
            print("❌ Could not parse JSON. Returning empty list.")
            return []
    except Exception as e:
        print(f"❌ ERROR during summarization: {str(e)}")
        return []


def save_json_to_csv(data, file_name):
    """
    Save FAQ data to a CSV file.
    
    Args:
        data (list): List of FAQ dictionaries
        file_name (str): Output CSV file path
    """
    print(f"{'='*60}")
    print(f"💾 SAVING RESULTS TO CSV")
    print(f"{'='*60}\n")
    
    if not data:
        print("⚠️  WARNING: No data to save!")
        return
    
    try:
        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            # Get the keys (column names) from the first dictionary
            fieldnames = data[0].keys()
            
            # Create a CSV dict writer object
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write the header row
            writer.writeheader()
            
            # Write the data rows with progress bar
            for entry in tqdm(data, desc="Writing FAQs", unit=" FAQs", ncols=80):
                writer.writerow(entry)
        
        print(f"\n✅ Successfully saved {len(data)} FAQs to '{file_name}'\n")
        
    except Exception as e:
        print(f"❌ ERROR saving CSV: {str(e)}")
        sys.exit(1)


def main():
    """
    Main function to orchestrate the FAQ extraction process.
    """
    print("\n" + "="*60)
    print("🚀 FAQ EXTRACTION FROM EMAIL REPLIES (JSON)")
    print("="*60)
    print("Using Ollama: qwen2.5:14b-instruct-q4_K_M")
    print("="*60 + "\n")
    
    # Configuration
    input_json = "generated_email_pairs.json"
    output_csv = "faq_json.csv"
    
    # Step 1: Load JSON file
    past_emails = load_json(input_json)
    
    # Step 2: Extract Zubair's replies
    print(f"{'='*60}")
    print(f"📧 EXTRACTING EMAIL REPLIES")
    print(f"{'='*60}\n")
    
    zubairs_replies = []
    for entry in tqdm(past_emails, desc="Extracting replies", unit=" emails", ncols=80):
        if isinstance(entry, dict) and "reply" in entry and entry["reply"]:
            zubairs_replies.append(entry["reply"])
    
    print(f"\n✅ Extracted {len(zubairs_replies)} email replies\n")
    
    # Combine all replies into a single string
    # Use newlines to separate replies for better context
    zubairs_replies_string = "\n\n---\n\n".join(zubairs_replies)
    print(f"📊 Total combined text length: {len(zubairs_replies_string):,} characters\n")
    
    # Step 3: Extract FAQs
    faqs = extract_faq(zubairs_replies_string)
    
    # Step 4: Save results
    if faqs:
        save_json_to_csv(faqs, output_csv)
        
        print(f"{'='*60}")
        print(f"✨ PROCESS COMPLETE!")
        print(f"{'='*60}\n")
        print(f"📁 Output file: {output_csv}")
        print(f"📊 Total FAQs extracted: {len(faqs)}\n")
    else:
        print(f"\n⚠️  No FAQs were extracted. Please check the output above for errors.\n")


if __name__ == "__main__":
    main()

