import requests

def download_file(url, file_name):
    
    """
    Download a file from a URL and save it locally.
    
    Parameters:
    url (str): The URL to the file you want to download.
    file_name (str): The name of the file to save the downloaded content.
    """
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open the file in write-binary mode and save the content
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully: {file_name}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

# Example usage
url = "https://youtu.be/-V6PqtElbCA"
file_name = "spbnd.mp4"
download_file(url, file_name)