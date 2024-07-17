const app = Vue.createApp({
    data() {
        return {
            video_path: '',
            audio_path: '',
            subtitle_text: '',
            font_size: '',
            font_color: '',
            border_color: '',
            bg_color: '',
            position: '',
            result: '',
            video_url: '',
            // Nuevos elementos de estilo
            fonts: ['Arial-Bold', 'Helvetica-Bold', 'Verdana-Bold'],
            colors: ['#39FF14', '#FF00FF', '#00FFFF'],
            border_colors: ['#FF4500', '#32CD32', '#1E90FF'],
            bg_colors: ['#000000', '#FFFFFF', '#FF1493'],
            font_sizes: [24, 26, 28, 30, 32, 34, 36, 38, 40]
        }
    },
    created() {
        axios.get('/process_video')
            .then(response => {
                this.video_path = response.data.video_path;
                this.audio_path = response.data.audio_path;
                this.subtitle_text = response.data.subtitle_text;
                this.font_size = response.data.font_size;
                this.font_color = response.data.font_color;
                this.border_color = response.data.border_color;
                this.bg_color = response.data.bg_color;
                this.position = response.data.position;
            })
            .catch(error => {
                console.error("There was an error fetching the video data:", error);
            });
    },
    methods: {
        createVideo() {
            Swal.fire({
                title: 'Are you sure?',
                text: "You are about to create a video!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, create it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    axios.post('/process_video', 
                        {
                            video_path: this.video_path,
                            audio_path: this.audio_path,
                            subtitle_text: this.subtitle_text,
                            font_size: this.font_size,
                            font_color: this.font_color,
                            border_color: this.border_color,
                            bg_color: this.bg_color,
                            position: this.position
                        }

                        //`video_path=${this.video_path}&audio_path=${this.audio_path}&subtitle_text=${this.subtitle_text}&font_size=${this.font_size}&font_color=${this.font_color}&position=${this.position}&video_url=${this.video_url}`,
                        //{ headers: { 'content-type': 'application/x-www-form-urlencoded' } }
                    )    
                    .then(response => {
                        Swal.fire({
                            title: "Video Processed",
                            text: "Video has been successfully processed",
                            icon: "success"
                        });
                        this.video_url = response.data.video_url;
                    })
                    .catch(error => {
                        console.error("There was an error processing the video:", error);
                        Swal.fire({
                            title: "Error",
                            text: `${error.response.data}`,
                            icon: "error"
                        });
                    });
                }
            });
        }
    }
}).mount('#app');

        
            /*parsePosition() {
                // Parse the position input if it's in the correct JSON format, otherwise return as is
                try {
                    return JSON.parse(this.position);
                } catch (e) {
                    console.error("Invalid position format:", e);
                    return this.position;
                }
            },
            async processVideo() {
                const parsedPosition = this.parsePosition();
                try {
                    const response = await fetch('/process_video', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            video_path: this.video_path,
                            audio_path: this.audio_path,
                            subtitle_text: this.subtitle_text,
                            font_size: this.font_size,
                            font_color: this.font_color,
                            position: this.position
                        })
                    });
                    const data = await response.json();
                    console.log('Response data:', data); // Para depuración
                    this.result = data.message;
                    if (response.ok) {
                        console.log('Video procesado con éxito:', data);
                        this.video_url = data.video_url;
                        console.log('URL del video:', this.video_url);  // Asigna la URL del vide
                    } else {
                        console.error('Error al procesar el video:', data);
                    }
                } catch (error) {
                    console.error('Error de red:', error);
                    this.result = 'An error occurred';
                }
        }
        }
});*/
