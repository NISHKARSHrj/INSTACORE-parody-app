



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
                ${post.image ? (
                    post.image.endsWith(".mp4") || post.image.endsWith(".mov")
                    ? `<video controls class="post-img">
                        <source src="${post.image}" type="video/mp4">
                        </video>`
                        : `<img src="${post.image}" class="post-img">`
                    ) : ""}
                <div class = "post-footer">
                    <button class="like-btn" onclick="likePost(${post.id})"> ❤️ ${post.like_count} </button>
                    ${post.user_id == USER_ID ? `
                        <button class="like-btn" onclick = "editpost(${post.id}, '${post.content}')">✏️ edit</button>
                        <button class="like-btn" onclick="deletePost(${post.id})">
                        🗑 delete
                        </button>
                    ` : ""}
                </div>
            `
            container.appendChild(postl)
        })
    }catch(err){
        console.error(err)
        container.innerHTML = `<div class = "empty">failed to load posts</div>`
    }
}

async function fetchCurrentUser() {
  try {
    let res  = await fetch('/me');
    let data = await res.json();
 
    if (res.ok) {
      let initials = data.user_name.slice(0, 2).toUpperCase();
      document.getElementById('nav-avatar').textContent   = initials;
      document.getElementById('nav-username').textContent = data.user_name;
      document.getElementById('post-avatar').textContent  = initials;
    }
  } catch (e) {
    console.error('Could not fetch user info:', e);
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
    if (image){
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

async function likePost(postId) {
    await fetch("/like", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: USER_ID,
            post_id: postId })
    })
    load_posts()
}

// dltposts 

async function deletePost(postId) {
    await fetch("/dltposts", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            post_id: postId
        })
    })
    load_posts()

}

// image-preview

function previewImage(input){
    let preview = document.getElementById("img-preview")

    if (input.files && input.files[0]) {
        preview.src = URL.createObjectURL(input.files[0])
        preview.style.display = "block"
    }
    else {
        preview.style.display = 'none';
    }
}

// logout

async function logout() {
    await fetch("/logout")
    window.location.href = "/login"
}

// formatTime

function formatTime(ts) {
    let date = new Date(ts);
    return date.toLocaleString();
}

async function editpost(postId, oldContent) {
    let newContent = prompt("Edit your post:", oldContent);

    if (!newContent) return;

    await fetch("/editpost",{
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            post_id: postId,
            content: newContent
        })
    })
    load_posts()        
}



load_posts()