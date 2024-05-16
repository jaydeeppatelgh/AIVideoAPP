<!-- work_space.html -->
{% extends 'header.html' %}
{% load static %}
{% block content %}
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <!-- Add the Slick CSS and JS files -->
    <link rel="stylesheet" type="text/css"
        href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.js"></script>
    <link href="{% static 'css/custom.css' %}" rel="stylesheet">
   
    <!-- Contact Start -->  
    <div class="container-fluid py-5">
        <div class="container py-5">
            <div class="mx-auto text-center wow fadeIn" data-wow-delay="0.1s" style="max-width: 500px;">
                <div class="login-heading">Work-Space</div>
                <button type="button" class="navbar-toggler ms-auto me-0" data-bs-toggle="collapse" data-bs-target="#navbarCollapse">
                    <span class="navbar-toggler-icon"></span>
                </button>
            </div>
            <div class="row justify-content-center">
                <div class="col-lg-7">
                    <p class="text-center mb-4">The contact form is currently inactive. Get a functional and working contact form with Ajax & PHP in a few minutes. Just copy and paste the files, add a little code and you're done. <a href="https://htmlcodex.com/contact-form">Download Now</a>.</p>
                    <div class="wow fadeIn" data-wow-delay="0.3s">
                         <div class="loader-container" id="loaderContainer" style="display: none;">
                            <div class="loader-main">
                                <div id="loader" class="loader"></div>
                                <div id="loader-text" class="loader-text"></div>
                            </div>
                            <div id="progressBar">
                                <div id="progress"></div>
                                <div id="progressText">0%</div>
                            </div>
                        </div>
                        {% if msg %}
                            <p style="color: green;">{{msg}}</p>
                        {% elif msg1 %}
                            <p style="color: red;">{{msg1}}</p>
                        {% else %}
                            <p style="color: red;"></p>
                        {% endif %}
                        <form method="post" action="{% url 'work_space' pk=user.pk %}" enctype="multipart/form-data">
                            {% csrf_token %}
                            <!-- Your form fields go here -->
                            <div class="col-12 input-txt-to-create-vid">
                                <div class="form-floating">
                                    <textarea class="form-control" placeholder="Leave a text here" name="message" id="message" style="height: 150px"></textarea>
                                    <label for="message">Give Me A Text...</label>
                                </div>
                            </div>
                            <div class="col-12 input-txt-to-create-vid">
                                <button id="generateButton" class="btn btn-primary w-100 py-3 btn-to-mrg-vid" type="submit">Generate Video</button>  
                            </div>
                            {% if generated_text %}
                            <div class="loader-container">
                                <div class="loader-main">
                                <div id="loader" class="loader"></div>
                                    <div id="loader-text" class="loader-text"></div>
                                </div>
                                <div id="progressBar" style="display: none;">
                                    <div id="progress"></div>
                                    <div id="progressText">0%</div>
                                </div>
                            </div>
                            {% endif %}
                            {% if work_space_entry %}
                                <div class="mt-3">
                                    <h4>WorkSpace Entry Information:</h4>
                                    <p>User: {{ work_space_entry.user.name }}</p>
                                    <p>Message: {{ work_space_entry.message }}</p>
                                    <p>Generated Text: {{ work_space_entry.generated_text }}</p>
                                    <!-- <p>Video URL: <a href="{{ work_space_entry.video_url }}" target="_blank">{{ work_space_entry.video_url }}</a></p> -->
                                    <p>Date Created: {{ work_space_entry.created_at }}</p>
                                <!-- Add any other fields you want to display -->
                                </div>
                            {% endif %}

                            {% if merged_audio_and_video_path %}
                                <h3>Merged Video:</h3>
                                <video width="640" height="360" controls>
                                    <source src="{{ merged_audio_and_video_path|safe }}" type="video/mp4">
                                    Your browser does not support the video tag.
                                </video>
                            {% endif %} 
                            {% if user_work_space_entries %}
                                <h3>User's WorkSpace History:</h3>
                                    <ul>
                                        {% for entry in user_work_space_entries %}
                                        <li>
                                            <a href="{{ entry.video_url }}" target="_blank">{{ entry.message }}</a>
                                        </li>
                                        {% endfor %}
                                    </ul>
                            {% endif %}
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Contact End -->     
<script>
    $(document).ready(function () {
        $("form").submit(function () {
            // Show loader when form is submitted
            $("#loaderContainer").show();
            $("#generateButton").hide();
        });
    });
</script>
       
    {% endblock %}
