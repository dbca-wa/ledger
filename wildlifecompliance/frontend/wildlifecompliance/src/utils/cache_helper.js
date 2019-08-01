import localforage from "localforage";
import Vue from 'vue';

/*
 * localforage prefers IndexedDB storage, consisting of key/value pairs (npm install --save localforage)
 * localforage api ref: https://localforage.github.io/localForage/
 * Each store should be nested within a system-level db (dbName)
 * Cache expiry measured in milliseconds
 * key is based on a Django model "id" column, and must be passed to this method as a string
 * url retrieval logic targeted to Django REST Framework detail_route and list_route methods
 * all records are stored in an array [<timestamp>, <value>]
 * stores should be set either as a list (getSetCacheList) or as individual records (getSetCache)
 */
let dbName = 'WildlifeCompliance';
const timeNow = Date.now();
let expiryDiff = 86400000;  // 1 day = 86400000 milliseconds;


module.exports = {
    getSetCache: async (store_name, key, url, expiry) => {
        
        let storeInstance = localforage.createInstance({
            name: dbName,
            storeName: store_name,
          });
        if (expiry) {
            expiryDiff = expiry;
        }
        await storeInstance.ready();

        try {
            let retrieved_val = await storeInstance.getItem(
              key);
            if (retrieved_val) {
            
                let timeDiff = timeNow - retrieved_val[0];
                // ensure cached value is not stale
                if (timeDiff < expiryDiff) {
                    return retrieved_val[1];
                }
            }
            else {
                const returnedFromUrl = await Vue.http.get(url);
                // url returns individual record (eg. @detail_route)
                if (returnedFromUrl.body.id) {
                    // assumes that every record has an id element
                    let valToStore = [timeNow, returnedFromUrl.body];
                    let retrieved_val = await storeInstance.setItem(
                        returnedFromUrl.body.id.toString(),
                        valToStore
                    );
                    if (retrieved_val) {
                        return retrieved_val[1];
                    }
                } 
            }
            // ensure cached value is not stale (1 week based on default expiry date)
            let store_keys = await storeInstance.keys();
            if (store_keys.length > 0) {
                for (let store_key of store_keys) {
                    let this_entry = await storeInstance.getItem(store_key);
                    let timeDiff = timeNow - this_entry[0];
                    if (timeDiff > expiryDiff * 7) {
                        await storeInstance.removeItem(store_key);
                    }
                }
            }
        } catch(err) {
            // on cache failure, request data from backend directly
            const returnedFromUrl = await Vue.http.get(url);
            return returnedFromUrl.body;
        }
    },
    getSetCacheList: async (store_name, url, expiry) => {
        try {
            let returned_list = [];  
            if (expiry) {
                expiryDiff = expiry;
            }
            let storeInstance = localforage.createInstance({
                name: dbName,
                storeName: store_name,
            });

            let store_keys = await storeInstance.keys();
            // existing store
            if (store_keys.length > 0) {
                // Clear store if stale
                // We only need to check the first entry, since all store values are written at the same time
                let firstEntry = await storeInstance.getItem(store_keys[0]);
                let timeDiff = timeNow - firstEntry[0];
                // ensure cached value is not stale
                if (timeDiff > expiryDiff) {
                    storeInstance.clear();
                } else {
                    for (let store_key of store_keys) {
                        let this_val = await storeInstance.getItem(store_key);
                        if (this_val) {
                            returned_list.push(this_val[1]);
                        }
                    }
                }
            } 
            let fresh_keys = await storeInstance.keys();
            if (fresh_keys.length === 0) {
            // else {    
            // empty store - get data from url
                const returnedFromUrl = await Vue.http.get(url);
                // ensure store is empty
                await storeInstance.clear();
                // populate store - switch accounts for DRF method using @renderer_classes((JSONRenderer,))
                if (returnedFromUrl.body.results) {
                for (let record of returnedFromUrl.body.results) {
                    let new_val = await storeInstance.setItem(
                        record.id.toString(), 
                        [timeNow, record]
                        );
                    returned_list.push(new_val[1]);
                }
                } else {
                    for (let record of returnedFromUrl.body) {
                    let new_val = await storeInstance.setItem(
                        record.id.toString(), 
                        [timeNow, record]
                        );
                    returned_list.push(new_val[1]);
                }
                }
            }
            return returned_list;

        } catch(err) {
            // on cache failure, request data from backend directly
            const returnedFromDb = await Vue.http.get(url);
            if (returnedFromDb.body.results) {
                return returnedFromDb.body.results;
            } else {
                return returnedFromDb.body;
            }
        }
    }
};
