import streamlit as st
import requests
import json
import time
import base64

url = "https://glif.app/api/run-glif"
headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://glif.app',
    'referer': 'https://glif.app/glifs/cm09xr2b8000t2qz2bva95bhq/',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'cookie': 'cookiesAccepted=true; intercom-id-kly9b2fr=72c0da9b-ba97-43af-9e77-8c9fec49e544; intercom-session-kly9b2fr=; intercom-device-id-kly9b2fr=abdb6ea0-feec-4a21-bea3-b45079c6cb4f; **Host-next-auth.csrf-token=e2689f33e19f8e4cba4acde9fcbf3cf080033b2578bb617e0b20cd252861f14e%7C820416ecc1265b79bb8deca5285ea34d3f51f8b3c15913b932cb46d5bbeb36be; **Secure-next-auth.callback-url=https%3A%2F%2Fglif.app%2Fsignin%3FcallbackUrl%3Dhttps%253A%252F%252Fglif.app%252F%2540DATAN3RD%252Fglifs%252Fcm09di1sj0004femrvcggx81x%252Fedit; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..z4EYFvDhFr7alZVE.OuuvG2AVu_zpvmzndoBtKmwKjXEk6y8qSYSROi8vUCaRjENV76xKJXInKG4FiwKdLJYyebTtFeY_oWnsEnf6lHE8hz8eUx6GE0VrJUwDlXA8Cfo-C_nokiY7BIKY-cOVGqTsKluCDuV5AvJtowcLPJNRoKaSxRzbHmbe139ANkECB0H8sLZp0UArFBfRDmXb5G7VZieYoZO2MVo-qd9JpTmZn339wUYBoyWMlB5sPkT5Aq-T-DRG76_opgvaOxNNhy6KhzcWMufDil8cGCPwWXeiohOtDXLL4QVSudmCBpmT8L0QPO0wOA-0k0FVFGdnhLWu2sej9jIN1T99hkQJTqvXKYi60Q4IMqhBbanuqqaPFkd9r03eixkrtiUHTj3_n9EWFclgN-2ZeVAdlJGAVZTU5BwwqpLJJ8BWyjvIEkDLozg-uxH2Rcy79BS_y8esgCo2iAeZQaaBRjcjJi9R.Tr667qDUhdu9I1eCH7VYmQ'
}

st.title("DATAN3RD Image Generator")

def download_button(image_url, filename):
    response = requests.get(image_url)
    if response.status_code == 200:
        b64 = base64.b64encode(response.content).decode()
        href = f'<a href="data:image/jpeg;base64,{b64}" download="{filename}">Download Image</a>'
        return href
    return "Download failed"

prompt = st.text_area("Prompt", "")
width = st.text_input("Width", "1024")
height = st.text_input("Height", "1024")

if st.button("Generate"):
    start_time = time.time()
    prompt_used = ""
    completed_images = {}
    status = "running"
    prompt_displayed = False
    
    payload = {
        "id": "cm09xr2b8000t2qz2bva95bhq",
        "version": "draft",
        "inputs": {
            "input1": prompt,
            "width": width,
            "height": height
        },
        "glifRunIsPublic": False
    }
    
    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=300) as response:
            st.write("Response Status Code:", response.status_code)
            
            if response.status_code == 200:
                st.write("Generating images ...")
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            graph_state = data.get("graphExecutionState", {})
                            status = graph_state.get("status", "running")
                            
                            # Extract prompt when text1 is completed
                            if graph_state.get("nodes", {}).get("text1", {}).get("status") == "done" and not prompt_displayed:
                                prompt_used = graph_state["nodes"]["text1"]["output"]["value"]
                                st.write("Prompt Used:")
                                st.write(prompt_used)
                                prompt_displayed = True
                            
                            # Check for completed Comfy nodes
                            for node, node_data in graph_state.get("nodes", {}).items():
                                if node.startswith("comfy") and node_data.get("status") == "done" and node not in completed_images:
                                    output = node_data.get("output", {})
                                    if output.get("type") == "IMAGE":
                                        completed_images[node] = output["value"]
                                        st.image(output["value"], caption=f"Image {len(completed_images)}", use_column_width=True)
                                        st.markdown(download_button(output["value"], f"image{len(completed_images)}.jpg"), unsafe_allow_html=True)
                            
                            # Display current status
                            # st.write(f"Current status: {status}")
                            if status == "completed":
                                break
                            
                        except json.JSONDecodeError:
                            st.write(f"Non-JSON data received: {line}")
                    
                    if time.time() - start_time > 180:
                        st.write("3 minutes elapsed. Ending capture.")
                        break
            else:
                st.write("Unexpected status code. Response content:")
                st.code(response.text[:500])
        
        # Display final results
        if status == "completed":
            st.write("Total execution time: {:.2f} seconds".format(time.time() - start_time))
            st.write("Image generation complete.")
        
    except requests.exceptions.Timeout:
        st.error("The request timed out after 5 minutes.")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred during the request: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        import traceback
        st.code(traceback.format_exc())