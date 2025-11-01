import tweepy
import mysql.connector

# --- Twitter Authentication ---
client = tweepy.Client(
    consumer_key="s52D3uOMEpqK60fyJqFTf9mjh",
    consumer_secret="zJr1X1xQ2jcOGxUzEz6aLoInnLNTWhlcoNOnTrjLP0kybnVCNE",
    access_token="1304631574957142016-QKF3I04WoOX5yCO0D34W1R7gDTRtff",
    access_token_secret="tqmCrYfrREtehwTSB265kFEmHuG1LiZ9olLVzUIlJNjBQ"
)

# --- MySQL Connection ---
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",       
        database="twitter"
    )
    cur = conn.cursor()
    print("✅ Connected to MySQL Database")

    # Create table if it doesn’t exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tweet_text VARCHAR(280),
            tweet_id BIGINT,
            tweet_url VARCHAR(255)
        )
    """)
    conn.commit()

except Exception as e:
    print("❌ MySQL connection failed:", e)
    exit()

# --- Check Twitter Login ---
username = None
try:
    user = client.get_me()
    username = user.data.username
    print(f"✅ Logged in as: {username}")
except tweepy.errors.Unauthorized as e:
    print("❌ Authentication failed:", e)
    exit()


# === Function to Display Tweets ===
def display_tweets():
    """Display all tweets stored in the MySQL table."""
    cur.execute("SELECT * FROM tweets")
    print("\n=== Saved Tweets in Database ===")

    # Print column headers
    for col in cur.description:
        print(f'{col[0]:^20}', end='\t')
    print("\n" + "-" * 80)

    # Print each row
    for row in cur.fetchall():
        for value in row:
            print(f'{str(value):^20}', end='\t')
        print()
    print("-" * 80)


# === Post Tweet ===
def post_tweet():
    tweet_text = input("Enter your tweet: ")

    try:
        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data["id"]
        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

        print(f"✅ Tweet posted successfully!\n🔗 {tweet_url}")

        # Save in MySQL
        cur.execute(
            "INSERT INTO tweets (tweet_text, tweet_id, tweet_url) VALUES (%s, %s, %s)",
            (tweet_text, tweet_id, tweet_url),
        )
        conn.commit()
        print("🗄 Saved to MySQL Database")

    except tweepy.errors.Unauthorized:
        print("❌ Authentication failed — check your keys and tokens.")
    except Exception as e:
        print("⚠ Error posting tweet:", e)


# === Delete Tweet ===
def delete_tweet():
    display_tweets()
    tweet_id = input("\nEnter the Tweet ID to delete: ")

    try:
        client.delete_tweet(id=tweet_id)
        print("🗑 Tweet deleted successfully on Twitter!")

        # Remove from MySQL
        cur.execute("DELETE FROM tweets WHERE tweet_id = %s", (tweet_id,))
        conn.commit()
        print("🗄 Deleted from MySQL Database")

    except tweepy.errors.NotFound:
        print("❌ Tweet not found — check the ID.")
    except Exception as e:
        print("⚠ Error deleting tweet:", e)


# === Menu ===
if __name__ == "__main__":
    while True:
        print("\n=== Twitter Automation System (MySQL Only) ===")
        print("1️⃣ Post a Tweet")
        print("2️⃣ Delete a Tweet")
        print("3️⃣ View All Tweets (from Database)")
        print("4️⃣ Exit")

        choice = input("Choose an option (1/2/3/4): ")

        if choice == "1":
            post_tweet()
        elif choice == "2":
            delete_tweet()
        elif choice == "3":
            display_tweets()
        elif choice == "4":
            print("👋 Bye!")
            cur.close()
            conn.close()
            break
        else:
            print("❌ Invalid choice.")