import wikipedia
import os

# Set language to English (default)
wikipedia.set_lang("en")

def fetch_company_data(companies):
    corpus_content = ""
    
    for company in companies:
        print(f"Fetching data for {company}...")
        try:
            # Get the page content
            page = wikipedia.page(company, auto_suggest=False)
            
            # Format the content: Title followed by a summary/intro and first section
            content = f"### {page.title}\n{page.summary}\n\n"
            corpus_content += content
            print(f"  Successfully fetched {page.title}")
            
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"  Error: Disambiguation found for {company}. Suggestions: {e.options[:3]}")
        except wikipedia.exceptions.PageError:
            print(f"  Error: Page not found for {company}")
        except Exception as e:
            print(f"  An unexpected error occurred for {company}: {e}")

    return corpus_content

def main():
    # List of companies to fetch from Wikipedia
    companies_to_fetch = [
        "OpenAI",
        "Microsoft",
        "Google",
        "Tesla, Inc.",
        "Apple Inc.",
        "Nvidia"
    ]
    
    data = fetch_company_data(companies_to_fetch)
    
    output_path = "tech_company_corpus.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(data)
    
    print(f"\nSuccessfully saved Wikipedia data to {output_path}")

if __name__ == "__main__":
    main()
