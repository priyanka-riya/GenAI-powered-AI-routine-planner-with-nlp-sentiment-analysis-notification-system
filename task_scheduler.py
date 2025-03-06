from transformers import pipeline
from textblob import TextBlob

# Load Hugging Face model for prioritization
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def prioritize_tasks(tasks):
    """Uses NLP model to prioritize tasks based on urgency and importance."""
    labels = ["High Priority", "Medium Priority", "Low Priority"]
    
    task_priorities = {}
    for task in tasks:
        result = classifier(task, labels)
        priority = result["labels"][0]  # Highest probability label
        task_priorities[task] = priority

    # Sort tasks based on priority
    sorted_tasks = sorted(task_priorities.items(), key=lambda x: labels.index(x[1]))
    
    return [task[0] for task in sorted_tasks]

def analyze_sentiment(text):
    """Returns sentiment polarity (-1 to 1) of the given text."""
    sentiment_score = TextBlob(text).sentiment.polarity
    return sentiment_score

def update_priorities_based_on_sentiment(priority, sentiment):
    sentiment_mapping = {"Negative": -1, "Neutral": 0, "Positive": 1}  
    sentiment_score = sentiment_mapping.get(sentiment, 0)  # Convert 'Neutral' to 0 instead of float
    # Now use sentiment_score for priority adjustments


# Example usage
if __name__ == "__main__":
    sample_tasks = ["Submit project report", "Call mom", "Buy groceries", "Prepare for meeting"]
    sentiment = analyze_sentiment("I'm feeling a bit stressed today.")
    
    prioritized_tasks = prioritize_tasks(sample_tasks)
    adjusted_tasks = update_priorities_based_on_sentiment(prioritized_tasks, sentiment)

    print("Prioritized Tasks:", adjusted_tasks)
