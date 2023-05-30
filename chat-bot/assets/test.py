import csv
import random

def fetch_ratings():
    # Open the CSV file
    with open('genres.csv', 'r') as file:
        reader = csv.reader(file)
        # Create a dictionary to store the topics and their corresponding numbers
        topics = {}
        # Iterate over each row in the CSV file
        for row in reader:
            topic = row[0]
            number = int(row[1])
            # Add the topic and its number to the dictionary
            topics[topic] = number
        return topics

def init_ratings():
    # Read the topic scores from the CSV file
    topics = fetch_ratings()

    # Iterate over each topic and update its score
    for topic in topics:
        # Generate a random score between 4 and 8 (inclusive)
        new_score = random.randint(4, 8)
        change_rating(topic, new_score)

    print("Scores randomized successfully.")

def fav_genres():
    # Read the topic scores from the CSV file
    topics = fetch_ratings()

    # Sort the topics based on their scores in descending order
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)

    # Retrieve the top two topics
    top_topics = sorted_topics[:2]
    highest_scores = [score for _, score in top_topics]

    # Find additional topics with the same score as the top two topics
    result = [topic for topic, score in sorted_topics if score in highest_scores]

    return result

def categorize_genres():
    # Read the topic scores from the CSV file
    topics = fetch_ratings()

    # Sort the topics based on their scores in descending order
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)

    # Calculate the number of topics for each percentile
    total_topics = len(sorted_topics)
    top30_count = int(0.3 * total_topics)
    next30_count = int(0.6 * total_topics)

    # Initialize the arrays for each percentile
    top_genres = [] #Top 30% of genres
    mid_genres = [] #40-70% of genres
    avoid_genres = [] #Bottom 40% of genres

    # Iterate over the sorted topics and distribute them into the arrays
    for i, (topic, score) in enumerate(sorted_topics):
        if score == sorted_topics[0][1]:
            top_genres.append(topic)
        elif score == sorted_topics[-1][1]:
            avoid_genres.append(topic)
        elif i < top30_count:
            top_genres.append(topic)
        elif i < next30_count:
            mid_genres.append(topic)
        else:
            avoid_genres.append(topic)

    return top_genres, mid_genres, avoid_genres

def change_rating(topic, new_score):
    # Check if the new score is within the range of 1-10
    if new_score < 1 or new_score > 10:
        print("Invalid score. Score must be between 1 and 10.")
        return

    # Read the topic scores from the CSV file
    topics = fetch_ratings()

    # Find the topic in the dictionary and update its score
    if topic in topics:
        topics[topic] = new_score
    else:
        print("Topic not found.")
        return

    # Write the updated scores back to the CSV file
    with open('genres.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for topic, score in topics.items():
            writer.writerow([topic, score])

    print("Score updated successfully.")

def update_rating(topic, rating):
    # Read the topic scores from the CSV file
    topics = fetch_ratings()

    # Find the topic in the dictionary and retrieve its current score
    current_score = topics.get(topic)
    if current_score is None:
        print("Topic not found.")
        return

    # Update the score based on the rating input
    if rating == "favourite":
        new_score = 9
    elif rating == "love":
        new_score = min(current_score + 2, 10)
    elif rating == "like":
        new_score = min(current_score + 1, 10)
    elif rating == "dislike":
        new_score = max(current_score - 1, 1)
    elif rating == "strongly dislike":
        new_score = max(current_score - 2, 1)
    elif rating == "hate":
        new_score = 2
        change_rating(topic, new_score)
        return
    else:
        print("Invalid rating.")
        return

    # Update the score using the change_rating function
    change_rating(topic, new_score)

#example run

init_ratings()
on,tw,th = categorize_genres()
print("top 30 : ", on)
print("mid : ", tw)
print("avoid : ", th)


print("they listened to educational and loved it")
update_rating("Educational", "love")

on,tw,th = categorize_genres()
print("top 30 : ", on)
print("mid : ", tw)
print("avoid : ", th)

print("they listened to True Crime and hate it")
update_rating("True Crime", "hate")

print(fav_genres())

# read_rating(topic)
# Reads and returns the score of a specific genre from the CSV file.

# init_ratings()
# Randomly initializes the scores between 4 and 8 (inclusive) for all genres in the CSV file.

# fav_genres()
# Finds the top two genre with the highest scores, and additional genre with the same score.

# categorize_topics()
# Categorizes the genre into three arrays based on their scores: top 30%, next 30%, and bottom 40%.

# change_rating(topic, new_score)
# Updates the score of a specific genre in the CSV file.

# update_rating(topic, rating)
# Updates the score of a specific topic based on the given rating.

