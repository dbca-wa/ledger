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

module.exports = {
    getSetCache: async function(store_name, key, url, expiry) {
        
        let storeInstance = localforage.createInstance({
            name: dbName,
            storeName: store_name,
          });
        if (expiry) {
            expiryDiff = expiry;
        }
        
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
    },
    getSetCacheList: async function(store_name, url, expiry) {
        try {
            let returned_list = [];
            if (expiry) {
                expiryDiff = expiry;
            }
            let storeInstance = localforage.createInstance({
                name: dbName,
                storeName: store_name,
            });
            
            let keys = await storeInstance.keys();
            // existing store
            if (keys.length > 0) {
                // Clear store if stale
                // We only need to check the first entry, since all store values are written at the same time
                let firstEntry = await storeInstance.getItem(keys[0]);
                let timeDiff = timeNow - firstEntry[0];
                        // ensure cached value is not stale
                        if (timeDiff > expiryDiff) {
                            await storeInstance.clear();
                        }
            } else {
                // empty store - get data from url
                let returnedFromUrl = await Vue.http.get(url);
                // ensure store is empty
                await storeInstance.clear();
                // populate store
                if (returnedFromUrl) {
                returnedFromUrl.body
                .forEach(async (record) => {
                    await storeInstance.setItem(
                        record.id.toString(), 
                        [timeNow, record]
                        );
                });
                }
            }
            // Now populate the returned list from cache
            await storeInstance.iterate((value, key, iterationNumber) => {
                returned_list.push(value[1]);
            });
            return returned_list;
        } catch(err) {
            console.log(err);
        }
    }
};
