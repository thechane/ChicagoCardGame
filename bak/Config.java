package net.roadtrip2001.kivychicago;

import org.onepf.oms.OpenIabHelper;
import org.onepf.oms.SkuManager;

import java.util.HashMap;
import java.util.Map;


public final class Config {

    // SKUs for our products: the premium upgrade (non-consumable) and gas (consumable)
	//public static final String SKU_TESTPRODUCT = "net.roadtrip2001.kivychicago.test_product";
	public static final String SKU_NOADS = "net.roadtrip2001.kivychicago.noads";
	public static final String SKU_SWEDEN = "net.roadtrip2001.kivychicago.swedenflaggedcards";
	public static final String SKU_USA = "net.roadtrip2001.kivychicago.usaflaggedcards";
	public static final String SKU_UK = "net.roadtrip2001.kivychicago.ukflaggedcards";
	//public static final String SKU_PREMIUM = "fr.alborini.openiab4kivy.premium";
    //public static final String SKU_GAS = "fr.alborini.openiab4kivy.gas";
    //public static final String SKU_INFINITE_GAS = "fr.alborini.openiab4kivy.infinitegas";

    /**
     * Google play public key.
     */
    public static final String GOOGLE_PLAY_KEY= "_GOOGLEPLAYKEY_";
    public static final Map<String, String> STORE_KEYS_MAP;

    static {
        //STORE_KEYS_MAP = new HashMap<>();					//Java 7 SE only
        STORE_KEYS_MAP = new HashMap<String, String>();
        STORE_KEYS_MAP.put(OpenIabHelper.NAME_GOOGLE, Config.GOOGLE_PLAY_KEY);
	/*
        SkuManager.getInstance()
	    //.mapSku(SKU_INFINITE_GAS, OpenIabHelper.NAME_NOKIA, SKU_INFINITE_GAS_NOKIA_STORE)
	    //.mapSku(SKU_INFINITE_GAS, OpenIabHelper.NAME_YANDEX, SKU_INFINITE_GAS_YANDEX)
                .mapSku(SKU_INFINITE_GAS, OpenIabHelper.NAME_AMAZON, SKU_INFINITE_GAS_AMAZON)
	    //.mapSku(SKU_INFINITE_GAS, OpenIabHelper.NAME_APPLAND, SKU_INFINITE_GAS_APPLAND)
	    //.mapSku(SKU_INFINITE_GAS, OpenIabHelper.NAME_SLIDEME, SKU_INFINITE_GAS_SLIDEME)

	    //.mapSku(SKU_GAS, OpenIabHelper.NAME_NOKIA, SKU_GAS_NOKIA_STORE)
	    //.mapSku(SKU_GAS, OpenIabHelper.NAME_YANDEX, SKU_GAS_YANDEX)
                .mapSku(SKU_GAS, OpenIabHelper.NAME_AMAZON, SKU_GAS_AMAZON)
	    //.mapSku(SKU_GAS, OpenIabHelper.NAME_APPLAND, SKU_GAS_APPLAND)
	    //.mapSku(SKU_GAS, OpenIabHelper.NAME_SLIDEME, SKU_GAS_SLIDEME)

	    //.mapSku(SKU_PREMIUM, OpenIabHelper.NAME_NOKIA, SKU_PREMIUM_NOKIA_STORE)
	    //.mapSku(SKU_PREMIUM, OpenIabHelper.NAME_YANDEX, SKU_PREMIUM_YANDEX)
                .mapSku(SKU_PREMIUM, OpenIabHelper.NAME_AMAZON, SKU_PREMIUM_AMAZON)
	    //.mapSku(SKU_PREMIUM, OpenIabHelper.NAME_APPLAND, SKU_PREMIUM_APPLAND)
	    //.mapSku(SKU_PREMIUM, OpenIabHelper.NAME_SLIDEME, SKU_PREMIUM_SLIDEME)
	    ;
	*/

    }

    private Config() {
    }
}
