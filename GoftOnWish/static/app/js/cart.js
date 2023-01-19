const updateBtns = document.querySelectorAll(".update-cart")

for(let i=0;i<updateBtns.length;i++){
    updateBtns[i].addEventListener('click',()=>{
        let productId = updateBtns[i].getAttribute("data-product");
        let action = updateBtns[i].getAttribute("data-action");
        console.log('productId: ',productId,'action: ',action);

        console.log('User',user)
        if(user === 'AnonymousUser'){
            window.location = '/login/'
        }else{
            updateUserOrder(productId,action)
        }
    })
}

function updateUserOrder(productId,action){
    console.log("User is logged in ,sending data...");
    var url = '/update_item/'

    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken
        },
        body:JSON.stringify({'productId':productId,'action':action})
    })

    .then((response)=>{
        return response.json()
    })

    .then((data)=>{
        console.log('data:',data)
        location.reload()
    })
}