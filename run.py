import base64

# Base64 encoded string
base64_string = "PVlqTTNNVE00TXpNM0V6WHlNak53TVROZlJUTTNJRE0yRUROM0VETXdFVEw="

# Step 1: Decode the base64 string
decoded_string = base64.b64decode(base64_string).decode('utf-8')

# Step 2: Print the decoded string to see its format
print(f"Decoded string: {decoded_string}")

# Step 3: Assuming decoded string format is "channel_id-message_id"
argument = decoded_string.split("-")

# Step 4: Extract channel_id and message_id
if len(argument) == 2:
    channel_id = argument[0]
    message_id = argument[1]
    print(f"Channel ID: {channel_id}")
    print(f"Message ID: {message_id}")
else:
    print("Invalid decoded format.")
