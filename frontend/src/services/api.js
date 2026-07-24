import axios from "axios";


const api = axios.create({

    baseURL: "http://127.0.0.1:8000/api",

    headers: {
        "Content-Type": "application/json",
    },

});


// -------------------------
// Hosts
// -------------------------

export function getHosts(){

    return api
        .get("/hosts")
        .then(res => res.data);

}


export function addHost(data){

    return api
        .post("/hosts", data)
        .then(res => res.data);

}


export function deleteHost(id){

    return api
        .delete(`/hosts/${id}`)
        .then(res => res.data);

}


export function toggleHost(id){

    return api
        .patch(`/hosts/${id}/toggle`)
        .then(res => res.data);

}



// -------------------------
// Analytics
// -------------------------

export function getAnalytics(){

    return api
        .get("/analytics/summary")
        .then(res => res.data);

}

export function getFullAnalytics(){

    return api
        .get("/analytics/full")
        .then(res => res.data);

}


// -------------------------
// Reports
// -------------------------

export function getReport(){

    return api
        .get("/reports/")
        .then(res => res.data);

}



export default api;