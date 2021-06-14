new Vue({
  el: '#app',
  data: {
    file: '',
    url: null,
    language: null,
    summarizerate: 60,
    origin: null,
    summarized: null,
    translated: null,
    showModal: false,
    port: '8080',
    message: 'Removed contents'
  },
  computed: {
    countOrigin: function() {
      return this.origin.split(" ").length
    },
    countSummarize: function() {
      return this.summarized.split(" ").length
    },
    countTranslate: function() {
      return this.translated.split(" ").length
    },
  },
  methods: {
    handleFileUpload: function() {
      this.file = this.$refs.file.files[0];
    },
    clear: function(){
      this.origin = null
      this.summarized = null
      this.translated = null
    },
    getNews: function(){
      this.origin = null
      axios({
        method: "POST",
        url: "http://localhost:"+this.port+"/news",
        params: {
          url: this.url
        },
        header: {"content-type": "text/plain"}
      }).then(result => {
        this.origin = result.data
      })
      this.summarized = null
      this.translated = null
    },
    summarize: function(){
      axios({
        method: "POST",
        url: "http://localhost:"+this.port+"/abridge",
        params: {
          origin: this.origin.replace("\r", ""),
          summarizerate: this.summarizerate
        },
        header: {"content-type": "text/plain"}
      }).then(result => {
        this.summarized = result.data
      })
      this.summarized = null
      this.translated = null
    },
    translate: function(){
      axios({
        method: "POST",
        url: "http://localhost:"+this.port+"/translate",
        params: {
          summarized: this.summarized
        },
        header: {"content-type": "text/plain"}
      }).then(result => {
        this.translated = result.data
      })
    },
    upload: function(){
      let formData = new FormData()
      formData.append('file', this.file)
      this.origin = null
      axios.post('/upload',
        formData,
        {
          headers : {
            'Content-Type' : 'multipart/form-data'
          }
        }
      // be careful !!! : then(function(result)) doesn't work
      ).then((result) => {
        this.origin = result.data
      }).catch(function(){
        this.message = "file upload failed"
      });
      this.summarized = null
      this.translated = null
    }
  }
})