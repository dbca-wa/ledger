import localforage from "localforage";
import Vue from 'vue';

/*
 * localforage prefers IndexedDB storage, consisting of key/value pairs (npm install --save localforage)
 * localforage api ref: https://localforage.github.io/localForage/
 * Each store should be nested within a system-level db (dbName)
 * Cache expiry measured in milliseconds
 * key is based on a Django model "id" column, and must be passed to this method as a string
 * url retrieval logic targeted to Django REST Framework detail_route and list_route methods
 */

module.exports = {
    getOrSetCache: async function(store_name, key, url, expiry) {
        let dbName = 'WildlifeCompliance';
        
        let store = localforage.createInstance({
            name: dbName,
            storeName: store_name,
          });

        const timeNow = Date.now();
        let expiryDiff = 300000; // 5 mins // 1 day 86400000;
        if (expiry) {
            expiryDiff = expiry;
        }
        
        try {
            let retrieved_val = await store.getItem(
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
                if (returnedFromUrl.id) {
                    // assumes that every record has an id element
                    let retrieved_val = await store.setItem(
                        returnedFromUrl.id,
                        [timeNow, returnedFromUrl]
                    );
                    if (retrieved_val) {
                        return retrieved_val[1];
                    }
                } 
                // url returns list (eg. @list_route)
                else if (returnedFromUrl.results || key == null) {
                    // clear, then repopulate store
                    await store.clear();
                    for (record in returnedFromUrl.results) {
                        // assumes that every record has an id element
                        await store.setItem(
                            record.id, 
                            [timeNow, record]
                            );
                    }
                    // requested key should now be in the store
                    let retrieved_val = await store.getItem(
                        key);

                    if (retrieved_val) {
                        return retrieved_val[1];
                    }
                } 
            }
        } catch(err) {
            console.error(err);
        }
    },
};
