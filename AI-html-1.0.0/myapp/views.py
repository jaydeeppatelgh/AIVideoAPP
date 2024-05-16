import logging
from django.shortcuts import render, redirect
from .models import User,WorkSpace,Uploadfiles
from django.conf import settings
from django.core.mail import send_mail
import random
import requests
import json
import openai
import os
from django.urls import reverse
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
from moviepy.video.fx.all import resize
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from gtts import gTTS
from pydub import AudioSegment
from django.core.files import File

logging.basicConfig(level=logging.INFO)  # Set to logging.DEBUG for more detailed logs

PEXELS_API_KEY = "ypeI3O5kOBaEaADVqRmmxrd0E9JYkg8ztdRerqANZQLbPwLc4KfKXbj1"

# Replace with your OpenAI API key
API__KEY = "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"
openai.api_key = API__KEY  # Set the OpenAI API key

# Create your views here.
def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            msg1 = "email already exists..."
            return render(request, 'signup.html', {'msg1': msg1})
        except User.DoesNotExist:
            if request.POST['pswd'] == request.POST['cpswd']:
                User.objects.create(
                    name=request.POST['name'],
                    email=request.POST['email'],
                    pswd=request.POST['pswd'],
                )
                msg = "Signup Done..."
                return render(request, 'login.html', {'msg': msg})
            else:
                msg1 = "password and confirm password do not match..."
                return render(request, 'signup.html', {'msg1': msg1})
    else:
        return render(request, 'signup.html')

def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'], pswd=request.POST['pswd'])
            request.session['email'] = user.email
            request.session['pswd'] = user.pswd
            
            # Get the user's primary key (pk)
            user_pk = user.pk
            
            # Redirect to 'work_space' with the 'pk' parameter
            return redirect(reverse('work_space', kwargs={'pk': user_pk}))
        except User.DoesNotExist:
            msg1 = "email does not exist"
            return render(request, 'login.html', {'msg1': msg1})
    else:
        return render(request, 'login.html')

def logout(request):
    del request.session['email']
    return redirect('login')

def fpswd(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            subject = 'Forgot Password OTP'
            otp = random.randint(100000, 999999)
            message = f'Hi {user.name}, thank you for registering in my app, your OTP is: {otp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(subject, message, email_from, recipient_list)
            return render(request, 'verify_otp.html', {'email': user.email, 'otp': str(otp)})
        except User.DoesNotExist:
            msg1 = "you are not a registered user..."
            return render(request, 'fpswd.html', {'msg1': msg1})
    else:
        return render(request, 'fpswd.html')

def verify_otp(request):
    email = request.POST['email']
    uotp = request.POST['uotp']
    otp = request.POST['otp']
    if request.method == 'POST':
        if uotp == otp:
            return render(request, 'set_pswd.html', {'email': email})
        else:
            msg1 = "OTP doesn't match!!!"
            return render(request, 'verify_otp.html', {'msg1': msg1})
    else:
        return render(request, 'verify_otp.html')

def set_pswd(request):
    if request.method == "POST":
        email = request.POST['email']
        npswd = request.POST['npswd']
        cnpswd = request.POST['cnpswd']
        if npswd == cnpswd:
            user = User.objects.get(email=email)
            user.pswd = npswd
            user.save()
            return redirect('login')
        else:
            msg1 = "password and confirm password do not match..."
            return render(request, 'set_pswd.html', {'msg1': msg1})
    else:
        return render(request, 'set_pswd.html')

def generate_text(user_input_text):
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOWQzZWM0MWMtNDNmOS00NjI2LTllMGYtNWRjMjFhOGEyYjI1IiwidHlwZSI6ImFwaV90b2tlbiJ9.wHS_BTq_LmWc0VlKQSla91cpzmh1M27KJWzL-iwi138"}
    url = "https://api.edenai.run/v2/text/generation"
    payload = {
        "providers": "openai,cohere",
        "text": user_input_text,
        "temperature": 0.2,
        "max_tokens": 2000
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        generated_text = result.get('openai', {}).get('generated_text', None)
        if generated_text:
            return generated_text
        else:
            print("Error: Unable to fetch generated text from Eden AI.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error in text generation process: {e}")
        return None

def create_folder(user_input_text):
    # Replace spaces with underscores
    folder_name = user_input_text.replace(" ", "_")
    base_folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)

    # Check if the folder already exists
    if not os.path.exists(base_folder_path):
        os.makedirs(base_folder_path, exist_ok=True)
        return base_folder_path

    # If the folder already exists, append a suffix
    suffix = 1
    while True:
        folder_path = os.path.join(
            settings.MEDIA_ROOT, f"{folder_name}_{suffix}")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            return folder_path
        suffix += 1

def merge_videos(video_urls, folder_path, target_duration):
    video_clips = []
    common_width, common_height = None, None
    total_duration = 0

    while total_duration < target_duration:
        for i, video_url in enumerate(video_urls):
            if i >= 5 or total_duration >= target_duration:
                break

            video_response = requests.get(video_url, timeout=10)
            video_response.raise_for_status()
            video_filename = os.path.join(folder_path, f"output_video_{i + 1}.mp4")
            # video_file_name = os.path.basename(video_url).split('?')[0]
            video_file_path = os.path.join(folder_path, video_filename)

            with open(video_file_path, "wb") as f:
                f.write(video_response.content)

            video_clip = VideoFileClip(video_file_path)
            if common_width is None and common_height is None:
                common_width, common_height = video_clip.size
            video_clip_resized = video_clip.resize((common_width, common_height))
            video_clips.append(video_clip_resized)

            total_duration += video_clip.duration

    # Trim the last video clip to match the target duration
    if total_duration > target_duration:
        last_clip_duration = video_clips[-1].duration
        excess_duration = total_duration - target_duration
        trimmed_last_clip = video_clips[-1].subclip(0, last_clip_duration - excess_duration)
        video_clips[-1] = trimmed_last_clip

    merged_video_path = os.path.join(folder_path, "merged_video.mp4")

    try:
        final_clip = concatenate_videoclips(video_clips, method="compose")
        final_clip.write_videofile(
            merged_video_path, codec="libx264", fps=24, logger=None
        )
    except Exception as e:
        print(f"Error merging videos: {e}")
        raise

    return merged_video_path


def merge_audio_and_video(audio_path, video_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    video_clip = VideoFileClip(video_path)
    # Ensure audio duration matches or is shorter than video duration
    audio_duration = min(audio_clip.duration, video_clip.duration)
    audio_clip = audio_clip.subclip(0, audio_duration)
    # Set the duration of the video clip to match the audio duration
    video_clip = video_clip.set_duration(audio_duration)
    # Combine audio and video
    final_clip = video_clip.set_audio(audio_clip)
    # Write the merged audio and video to a file
    final_clip.write_videofile(
        output_path, codec="libx264", fps=24, logger=None)
    return output_path

def generate_audio(text, folder_path):

    url = f"https://api.edenai.run/v2/audio/text_to_speech"

    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOWQzZWM0MWMtNDNmOS00NjI2LTllMGYtNWRjMjFhOGEyYjI1IiwidHlwZSI6ImFwaV90b2tlbiJ9.wHS_BTq_LmWc0VlKQSla91cpzmh1M27KJWzL-iwi138"}

    payload = {
        "providers": "google,amazon",
        "language": "en-US",
        "option": "FEMALE",  # Change this to "MALE" or "FEMALE" as needed
        "text": text,
        "settings": {'google': 'en-US-Standard-C', 'amazon': 'en-US_Ivy_Standard'}
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        result = json.loads(response.text)
        google_audio_url = result['google']['audio_resource_url']
        audio_response = requests.get(google_audio_url)
        audio_data = audio_response.content

        audio_output_path = os.path.join(folder_path, "output.mp3")

        with open(audio_output_path, 'wb') as audio_file:
            audio_file.write(audio_data)

        print("Audio generation successful.")
        return audio_output_path

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_video_from_pexels(user_input_text):
    try:
        response = requests.get(f"https://api.pexels.com/videos/search?query={user_input_text}",
                                headers={"Authorization": PEXELS_API_KEY},
                                timeout=10)
        response.raise_for_status()
        videos = response.json()["videos"]

        # Filter only landscape videos (width > height)
        landscape_videos = [video for video in videos
                            if "video_files" in video and video["video_files"]
                            and video["width"] > video["height"]]

        # Get the URLs of the videos.
        video_urls = [video["video_files"][0]["link"]
                      for video in landscape_videos]
        return video_urls[:5]  # Return all the available videos
    except requests.exceptions.RequestException as e:
        print(f"Error fetching videos from Pexels: {e}")
        return []

def generate_audio_from_video(video_path, output_audio_path):
    try:
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio_path)
        video_clip.close()
        return output_audio_path
    except Exception as e:
        print(f"Error generating audio from video: {e}")
        return None

def split_video_into_segments_with_audio(video_path, output_folder, segment_duration=20):
    os.makedirs(output_folder, exist_ok=True)

    video_clip = VideoFileClip(video_path)
    total_duration = video_clip.duration
    num_segments = int(total_duration // segment_duration)

    segment_urls = []
    segment_audio_paths = []

    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        segment = video_clip.subclip(start_time, end_time)

        segment_filename = f"segment_{i + 1}.mp4"
        segment_filepath = os.path.join(output_folder, segment_filename)
        segment.write_videofile(segment_filepath, codec="libx264", audio_codec="aac")

        # Generate audio from the video segment
        output_audio_path = os.path.join(output_folder, f"segment_{i + 1}.mp3")
        audio_path = generate_audio_from_video(segment_filepath, output_audio_path)
        
        if audio_path:
            # Construct the URL for the segment audio using MEDIA_URL
            relative_audio_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
            segment_audio_paths.append(os.path.join(settings.MEDIA_URL, relative_audio_path))

        # Construct the URL for the segment video using MEDIA_URL
        relative_path = os.path.relpath(segment_filepath, settings.MEDIA_ROOT)
        segment_urls.append(os.path.join(settings.MEDIA_URL, relative_path))

    # Handle the remaining duration
    remaining_duration = total_duration % segment_duration
    if remaining_duration > 0:
        start_time = num_segments * segment_duration
        remaining_segment = video_clip.subclip(start_time, total_duration)
        remaining_filename = f"segment_{num_segments + 1}.mp4"
        remaining_filepath = os.path.join(output_folder, remaining_filename)
        remaining_segment.write_videofile(
            remaining_filepath, codec="libx264", audio_codec="aac")

        # Generate audio from the remaining segment
        output_audio_path = os.path.join(output_folder, f"segment_{num_segments + 1}.mp3")
        audio_path = generate_audio_from_video(remaining_filepath, output_audio_path)

        if audio_path:
            # Construct the URL for the remaining segment audio using MEDIA_URL
            relative_audio_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
            segment_audio_paths.append(os.path.join(settings.MEDIA_URL, relative_audio_path))

        # Construct the URL for the remaining segment using MEDIA_URL
        relative_path = os.path.relpath(
            remaining_filepath, settings.MEDIA_ROOT)
        remaining_segment_url = os.path.join(settings.MEDIA_URL, relative_path)
        segment_urls.append(remaining_segment_url)

    video_clip.close()

    return segment_audio_paths

def split_video_into_segments(video_path, output_folder, segment_duration=20):
    os.makedirs(output_folder, exist_ok=True)

    video_clip = VideoFileClip(video_path)
    total_duration = video_clip.duration
    num_segments = int(total_duration // segment_duration)

    segment_urls = []

    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration
        segment = video_clip.subclip(start_time, end_time)

        segment_filename = f"segment_{i + 1}.mp4"
        segment_filepath = os.path.join(output_folder, segment_filename)
        segment.write_videofile(
            segment_filepath, codec="libx264", audio_codec="aac")

        # Construct the URL for the segment using MEDIA_URL
        relative_path = os.path.relpath(segment_filepath, settings.MEDIA_ROOT)
        segment_url = os.path.join(settings.MEDIA_URL, relative_path)
        segment_urls.append(segment_url)

    # Handle the remaining duration
    remaining_duration = total_duration % segment_duration
    if remaining_duration > 0:
        start_time = num_segments * segment_duration
        remaining_segment = video_clip.subclip(start_time, total_duration)
        remaining_filename = f"segment_{num_segments + 1}.mp4"
        remaining_filepath = os.path.join(output_folder, remaining_filename)
        remaining_segment.write_videofile(
            remaining_filepath, codec="libx264", audio_codec="aac")

        # Construct the URL for the remaining segment using MEDIA_URL
        relative_path = os.path.relpath(
            remaining_filepath, settings.MEDIA_ROOT)
        remaining_segment_url = os.path.join(settings.MEDIA_URL, relative_path)
        segment_urls.append(remaining_segment_url)

    video_clip.close()

    return segment_urls

def transcribe_audio_to_text(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai.Audio.transcribe(
                file=audio_file,
                model="whisper-1",
                response_format="text",
                language="en",  # Use ISO-639-1 format for English
            )

            print(response)  # Print the response for debugging

            # Assuming response is a string containing the transcribed text
            transcript = response

            # Create a counter to generate unique filenames
            counter = 1

            # Save the transcript to a text file with a unique name
            while True:
                text_file_name = f"transcript_{counter}.txt"
                text_file_path = os.path.join(os.path.dirname(audio_file_path), text_file_name)
                if not os.path.exists(text_file_path):
                    break
                counter += 1

            with open(text_file_path, "w") as text_file:
                text_file.write(transcript)
            print(text_file_path)
            return text_file_path
    except Exception as e:
        print(f"Error transcribing audio to text: {e}")
        return None    

def work_space(request, pk):
    segment_urls =[]
    segment_texts = []
    if request.method == 'POST':
        user_input_text = request.POST.get('message', '')
        generated_text = generate_text(user_input_text)
        folder_path = create_folder(user_input_text)
        video_urls = get_video_from_pexels(user_input_text)
        
        try:
            generated_audio_path = generate_audio(generated_text, folder_path)
        except Exception as e:
            print(f"Error in audio generation process: {e}")
            generated_audio_path = None
        # Initialize merged_audio_and_video_path to None
        merged_audio_and_video_path = None
        # Handle file upload
        uploaded_file = request.FILES.get('file_upload')
        if uploaded_file:
            # Save the uploaded file to a specific folder
            file_path = os.path.join(folder_path, uploaded_file.name)
            default_storage.save(file_path, ContentFile(uploaded_file.read()))
            # Now, you can use 'file_path' as needed
            # ...
        # Save the generated text and video URL to the WorkSpace model
        user = User.objects.get(email=request.session['email'])
        work_space_entry = WorkSpace.objects.create(
            user=user,
            message=user_input_text,
            generated_text=generated_text,
            video_url=merged_audio_and_video_path  # Change this to the actual video URL
        )
        # # Download and save the videos from Pexels (if available)
        # video_clips = []
        # common_width, common_height = None, None
        # for i, video_url in enumerate(video_urls):
        #     video_filename = os.path.join(folder_path, f"output_video_{i + 1}.mp4")
        #     try:
        #         response = requests.get(video_url, stream=True, timeout=10)
        #         response.raise_for_status()
        #         with open(video_filename, 'wb') as video_file:
        #             for chunk in response.iter_content(chunk_size=8192):
        #                 video_file.write(chunk)
        #         print(f"Video {i + 1} download successful.")
        #         video_clip = VideoFileClip(video_filename)
        #         # Resize the video to common width and height
        #         if common_width is None and common_height is None:
        #             common_width, common_height = video_clip.size
        #         video_clip_resized = resize(video_clip, width=common_width, height=common_height)
        #         video_clips.append(video_clip_resized)
        #     except requests.exceptions.RequestException as e:
        #         print(f"Error downloading video {i + 1} from Pexels: {e}")
        # # Merge videos
        # segment_texts = []
        # merged_video_path = os.path.join(folder_path, "merged_video.mp4")
        # try:
        #     final_video_clip = concatenate_videoclips(video_clips, method="compose")
        #     final_video_clip.write_videofile(merged_video_path, codec="libx264", fps=24, logger=None)
        # except Exception as e:
        #     print(f"Error merging videos: {e}")
        #     merged_video_path = None
        target_duration = 180
        merged_video_path = merge_videos(video_urls, folder_path, target_duration)
        # Merge audio and video
        if generated_audio_path and merged_video_path:
            output_path = os.path.join(folder_path, f"{user_input_text}.mp4")
            try:
                merged_audio_and_video_path = merge_audio_and_video(generated_audio_path, merged_video_path, output_path)
                relative_path = os.path.relpath(merged_audio_and_video_path, settings.MEDIA_ROOT)
                output_folder = os.path.join(folder_path, 'video_segments')
                segment_urls = split_video_into_segments(
                    merged_audio_and_video_path, output_folder, segment_duration=20)
                segment_audio_urls = split_video_into_segments_with_audio(
                    merged_audio_and_video_path, output_folder, segment_duration=20)

                # Transcribe each segment audio to text and save the text in the same folder
                for i, audio_url in enumerate(segment_audio_urls):
                        audio_path = os.path.join(settings.MEDIA_ROOT, os.path.relpath(audio_url, settings.MEDIA_URL))
                        output_text_file_path = transcribe_audio_to_text(audio_path)  # Fix here
                        if output_text_file_path:
                            with open(output_text_file_path, 'r') as text_file:
                                segment_text = text_file.read()
                                segment_texts.append(segment_text)
            except Exception as e:
                print(f"Error merging audio and video: {e}")
                merged_audio_and_video_path = None
                segment_audio_urls = []
        else:
            output_path = None
        
        upload_files_entry = Uploadfiles.objects.create(
            user=user,
            workspace=work_space_entry,
            segment_url_1=segment_urls[0] if segment_urls and len(segment_urls) > 0 else None,
            segment_url_2=segment_urls[1] if segment_urls and len(segment_urls) > 1 else None,
            segment_url_3=segment_urls[2] if segment_urls and len(segment_urls) > 2 else None,
            segment_url_4=segment_urls[3] if segment_urls and len(segment_urls) > 3 else None,
            segment_url_5=segment_urls[4] if segment_urls and len(segment_urls) > 4 else None,
            segment_url_6=segment_urls[5] if segment_urls and len(segment_urls) > 5 else None,
            segment_url_7=segment_urls[6] if segment_urls and len(segment_urls) > 6 else None,
            segment_url_8=segment_urls[7] if segment_urls and len(segment_urls) > 7 else None,
            segment_url_9=segment_urls[8] if segment_urls and len(segment_urls) > 8 else None,
            segment_text_1=segment_texts[0] if segment_texts and len(segment_texts) > 0 else None,
            segment_text_2=segment_texts[1] if segment_texts and len(segment_texts) > 1 else None,
            segment_text_3=segment_texts[2] if segment_texts and len(segment_texts) > 2 else None,
            segment_text_4=segment_texts[3] if segment_texts and len(segment_texts) > 3 else None,
            segment_text_5=segment_texts[4] if segment_texts and len(segment_texts) > 4 else None,
            segment_text_6=segment_texts[5] if segment_texts and len(segment_texts) > 5 else None,
            segment_text_7=segment_texts[6] if segment_texts and len(segment_texts) > 6 else None,
            segment_text_8=segment_texts[7] if segment_texts and len(segment_texts) > 7 else None,
            segment_text_9=segment_texts[8] if segment_texts and len(segment_texts) > 8 else None,
        )

        # Update the WorkSpace model with the actual video URL
        work_space_entry.video_url = os.path.join(settings.MEDIA_URL, relative_path)
        work_space_entry.upload_files_entry = upload_files_entry
        work_space_entry.save()
        
        user = User.objects.get(email=request.session['email'])
        user_work_space_entries = WorkSpace.objects.filter(user=user)
        return render(request, 'work_space.html', {
            'pk': pk,
            'user': user,
            'generated_text': generated_text,
            'generated_audio_path': generated_audio_path,
            'video_urls': video_urls,
            'user_input_text': user_input_text,
            'work_space_entry': work_space_entry,
            'video_filenames': [os.path.join(folder_path, f"output_video_{i + 1}.mp4") for i in range(len(video_urls))],
            'merged_video_path': merged_video_path,
            'merged_audio_and_video_path': os.path.join(settings.MEDIA_URL, relative_path),
            'user_work_space_entries': user_work_space_entries,
            'segment_urls': segment_urls,
            'segment_texts': segment_texts,  # Pass user's WorkSpace entries to the template
        })
    else:
        user = User.objects.get(email=request.session['email'])
        user_work_space_entries = WorkSpace.objects.filter(user=user)
        return render(request, 'work_space.html', {
            'pk': pk,
            'user': user,
            'user_work_space_entries': user_work_space_entries,
        })
def user_history(request, pk):
    # Your view logic goes here
    return render(request, 'user_history.html', {'pk': pk})

def delete_segment(request, workspace_pk, segment_index):
    if request.method == 'DELETE':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            segment_url = data.get('segment_url', '')

            workspace = get_object_or_404(WorkSpace, pk=workspace_pk)
            upload_file = get_object_or_404(Uploadfiles, workspace=workspace)

            # Determine the field name based on the segment index
            field_name = f'segment_url_{segment_index + 1}'

            # Get the current value of the field
            current_value = getattr(upload_file, field_name, None)

            if current_value == segment_url:
                # If the current value matches the provided URL, delete it
                setattr(upload_file, field_name, None)
                upload_file.save()

                return JsonResponse({'success': True, 'message': 'Segment deleted successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Segment URL does not match the record'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def update_segment_texts(request, workspace_pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.POST.get('updated_texts', '{}'))
            workspace = get_object_or_404(WorkSpace, pk=workspace_pk)
            upload_file = get_object_or_404(Uploadfiles, workspace=workspace)

            for segment_index, segment_text in data.items():
                field_name = f'segment_text_{segment_index}'
                setattr(upload_file, field_name, segment_text)

            upload_file.save()

            return JsonResponse({'success': True, 'message': 'Segment texts updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def upload_video(request, pk):
    if request.method == 'POST':
        segment_number = int(pk)
        uploaded_file = request.FILES.get('video_upload')

        if uploaded_file:
            # Save the uploaded file to the corresponding field in the Uploadfiles model
            user = User.objects.get(email=request.session['email'])
            work_space_entry = WorkSpace.objects.filter(user=user).last()
            upload_files_entry = Uploadfiles.objects.filter(workspace=work_space_entry).last()

            # Determine the field name based on the segment number
            field_name = f'upload_video_{segment_number}'
            setattr(upload_files_entry, field_name, uploaded_file)
            upload_files_entry.save()
            
            url_field_name = f'segment_url_{segment_number}'
            setattr(upload_files_entry, url_field_name, '')
            upload_files_entry.save()

            return JsonResponse({'success': True, 'message': f'Video for Segment {segment_number} uploaded successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'No file uploaded'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}) 
        
def merge_uploaded_videos(workspace, static_prefix="/var/www/html/AI-html-1.0.0"):
    try:
        # Get the latest Uploadfiles entry associated with the workspace
        upload_files_entry = Uploadfiles.objects.filter(workspace=workspace).last()

        # Create a list to store VideoFileClip objects and text
        video_clips = []
        text_clips = []

        # Fetch video paths and text from the segment_url and segment_text fields
        for i in range(1, 10):  # Assuming there are 9 segment_url fields
            field_url_name = f'segment_url_{i}'
            field_text_name = f'segment_text_{i}'

            video_path = getattr(upload_files_entry, field_url_name, None)
            text = getattr(upload_files_entry, field_text_name, None)

            if video_path:
                # Add the static prefix to the video path
                video_path_with_prefix = static_prefix + video_path

                # Check if the file exists before creating VideoFileClip
                if os.path.exists(video_path_with_prefix):
                    video_clip = VideoFileClip(video_path_with_prefix)
                    video_clips.append(video_clip)
                else:
                    print(f"File not found: {video_path_with_prefix}")

            if text:
                text_clips.append(text)

        # Reset the text variable for the second loop
        text = None

        # Fetch video paths from the upload_video fields dynamically
        for i in range(1, 10):  # Assuming there are 9 upload_video fields
            field_name = f'upload_video_{i}'
            video_file = getattr(upload_files_entry, field_name, None)

            if video_file and os.path.exists(video_file.path):
                # Create VideoFileClip from the upload_video file
                video_clip = VideoFileClip(video_file.path)
                video_clips.append(video_clip)
            else:
                print(f"No video found in {field_name}")

        # Merge the text clips
        merged_text = "\n".join(text_clips)

        # Convert merged text to speech and save as audio file
        tts = gTTS(text=merged_text, lang='en')
        audio_file_path = '/var/www/html/AI-html-1.0.0/media/music/edited_audio.mp3'
        
        # Determine the output audio file path with index
        base_audio_file_path = audio_file_path.replace('.mp3', '')
        index = 1
        while os.path.exists(audio_file_path):
            audio_file_path = f"{base_audio_file_path}_{index}.mp3"
            index += 1

        tts.save(audio_file_path)

        # Load the audio file as an AudioFileClip
        audio_clip = AudioFileClip(audio_file_path)

        # Determine the duration of the audio and video
        audio_duration = audio_clip.duration
        video_duration = sum([clip.duration for clip in video_clips])

        # Extend or trim the video to match the audio duration
        num_loops = int(audio_duration / video_duration) + 1
        final_video_clips = video_clips * num_loops
        final_video = concatenate_videoclips(final_video_clips, method="compose")

        # Trim the final video to match the audio duration
        final_video = final_video.subclip(0, audio_duration)

        # Set the audio of the final video
        final_video = final_video.set_audio(audio_clip)

        # Determine the output video file path with index
        base_output_path = "/var/www/html/AI-html-1.0.0/media/videos/edited_video"
        output_path = f"{base_output_path}.mp4"

        index = 1
        while os.path.exists(output_path):
            output_path = f"{base_output_path}_{index}.mp4"
            index += 1

        # Save the merged video to a file
        final_video.write_videofile(output_path, codec="libx264", fps=24, logger=None)
        relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
        segment_url = os.path.join(settings.MEDIA_URL, relative_path)
        # Save the video file to the edited_video field
        edited_video_file = open(output_path, "rb")
        upload_files_entry.edited_video.save(os.path.basename(output_path), File(edited_video_file))
        edited_video_file.close()
        print(f"Final def_path: {relative_path}")
        print(f"Final abc_path: {segment_url}")
        # Return the path of the merged video
        return segment_url

    except Exception as e:
        print(f"Error merging uploaded videos: {e}")
        return None
        
def merge_edited_audio_video(request, pk):
    try:
        user = User.objects.get(email=request.session['email'])
        workspace = WorkSpace.objects.filter(user=user).last()

        # Call the function to merge uploaded videos
        merged_edited_video = merge_uploaded_videos(workspace)

        if merged_edited_video:
            # Pass the merged video path to the template
            return JsonResponse({'success': True, 'message': 'Videos merged successfully', 'merged_edited_video': merged_edited_video})
        else:
            return JsonResponse({'success': False, 'message': 'Error merging videos'})

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User does not exist'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'})

