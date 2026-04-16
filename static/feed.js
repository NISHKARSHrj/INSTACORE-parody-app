// load poast on feed

async function load_posts() {
    let container = document.getElementById("posts-container")
    let loading = document.getElementById("feed-loading")

    try{
        let res = await fetch("/posts")
        let posts = await res.json()

        container.innerHTML = ""
        if (posts.length === 0){
            container.innerHTML = `<div class="empty">No posts yet.</div>`
            return
        }
        posts.forEach(post => {
            let postl = document.createElement("div")
            postl.className = "post-card"

            postl.innerHTML = `
                <div class = "post-head">
                    <div class = "post-avatar">${post.user[0]}</div>
                    <div class = "post-username">${post.user}</div>
                    <div class = "post-time">${formatTime(post.timestamp)}</div>
                </div>
                <div class="post-content">${post.content || ""}</div>
                ${post.image ? `<img src="/static/uploads/${post.image}" class="post-img">` : ""}
                <div class = "post-footer">
                    <button class="like-btn" onclick="likePost(${post.id})"> ❤️ ${post.like_count} </button>
                </div>
            `
            container.appendChild(postl)
        })
    }catch(err){
        container.innerHTML = `<div class = "empty">failed to load poats</div>`
    }
}

// create posts

async function createPost() {
    let content = document.getElementById("post-content").value
    let image = document.getElementById("img-input").files[0]
    let error = document.getElementById("post-error")

    let formdata = new FormData()
        formdata.append("user_id", USER_ID)
        formdata.append("content", content)
        if (iamge){
            formdata.append("image", image)
        }
    
    try{
        let res = await fetch("/posts", {
            method: "POST",
            body: formdata
        })
        if (!res.ok){
            let data = await res.json()
            error.textContent = data.error
            error.style.display = "block"
            return
        }

        document.getElementById("post-content").value = "" 
        document.getElementById("img-input").value = "" 
        document.getElementById("img-preview").style.display = "none"
        error.style.display = "none"

        load_posts()


    }catch (err){
        error.innerText = "failed to create post"
        error.style.display = "block"
    }
    
}

// like posts
