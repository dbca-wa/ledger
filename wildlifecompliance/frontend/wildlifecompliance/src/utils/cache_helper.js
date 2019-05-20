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
let expiryDiff = 300000;  // 1 day = 86400000 milliseconds;

//module.exports = {
    export async function getSetCache(store_name, key, url, expiry) {
        
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
                let returnedFromUrl = await Vue.http.get(url);
                console.log("returnedFromUrl");
                console.log(returnedFromUrl);
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
        } catch(err) {
            console.error(err);
        }
    }
    export async function getSetCacheList(store_name, url, expiry) {
        
        try {
            let returned_list = [];
            if (expiry) {
                expiryDiff = expiry;
            }
            let storeInstance = localforage.createInstance({
                name: dbName,
                storeName: store_name,
            });
            await storeInstance.ready();

            let store_keys = await storeInstance.keys();
            // existing store
            if (store_keys.length > 0) {
                // Clear store if stale
                // We only need to check the first entry, since all store values are written at the same time
                let firstEntry = await storeInstance.getItem(store_keys[0]);
                console.log("firstEntry");
                console.log(firstEntry);
                let timeDiff = timeNow - firstEntry[0];
                // ensure cached value is not stale
                if (timeDiff > expiryDiff) {
                    store_keys.forEach(async (store_key) => {
                        await storeInstance.removeItem(store_key);
                    });
                    //await storeInstance.ready();
                } else {
                    store_keys.forEach(async (store_key) => {
                        let this_val = await storeInstance.getItem(store_key);
                        if (this_val) {
                            returned_list.push(this_val[1]);
                        }
                    });
                }
                // await storeInstance.iterate((value, key, iterationNumber) => {
                //     returned_list.push(value[1]);
                // });
            
            } 
            await storeInstance.ready();
            store_keys = await storeInstance.keys();
            console.log("store_keys");
            console.log(store_keys);
            if ((store_keys.length == 0)) {
                // empty store - get data from url
                let returnedFromUrl = await Vue.http.get(url);
                console.log("returnedFromUrl");
                console.log(returnedFromUrl);
                // ensure store is empty
                //await storeInstance.clear();
                //await storeInstance.ready();
                // populate store - switch accounts for DRF method using @renderer_classes((JSONRenderer,))
                if (returnedFromUrl.body.results) {
                returnedFromUrl.body.results
                .forEach(async (record) => {
                    let valToStore = [timeNow, record];
                    let new_val = await storeInstance.setItem(
                        record.id.toString(), 
                        valToStore
                        );
                    returned_list.push(new_val[1]);
                });
                
                } else {
                    returnedFromUrl.body
                    .forEach(async (record) => {
                        let valToStore = [timeNow, record];
                        let new_val = await storeInstance.setItem(
                        record.id.toString(), 
                        valToStore
                        );
                    returned_list.push(new_val[1]);
                });
                }
                
            }
            // Ensure cached records are available to read
            //await storeInstance.ready();
            // Now populate the returned list from cache
            // await storeInstance.iterate((value, key, iterationNumber) => {
            //     returned_list.push(value[1]);
            // });
            // console.log(returned_list);        
            // return returned_list;   
                
            await storeInstance.ready();
            console.log("returned_list");
            console.log(returned_list);
            return returned_list;

        } catch(err) {
            console.log(err);
        }
}

//export { getSetCache, getSetCacheList };
