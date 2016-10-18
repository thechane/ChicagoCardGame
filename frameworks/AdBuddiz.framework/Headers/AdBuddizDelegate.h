//
//  AdBuddizDelegate.h
//  Copyright (c) 2015 Purple Brain. All rights reserved.
//

typedef enum {
    UNSUPPORTED_IOS_SDK = 0,
	CONFIG_NOT_READY = 1,
	CONFIG_EXPIRED = 2,
	MISSING_PUBLISHER_KEY = 3,
	INVALID_PUBLISHER_KEY = 4,
	PLACEMENT_BLOCKED = 5,
    PLATFORM_MISMATCH_PUBLISHER_KEY = 11,
	NO_NETWORK_AVAILABLE = 6,
    FORBIDDEN_RECEIVED_FROM_NETWORK = 12,
	NO_MORE_AVAILABLE_ADS = 8,
    AD_IS_ALREADY_ON_SCREEN = 10,
    
    //Exclusive to interstitial ad
    NO_MORE_AVAILABLE_CACHED_ADS = 7,
    SHOW_AD_CALLS_TOO_CLOSE = 9,
    
    //Exclusive to rewarded video
    NETWORK_TOO_SLOW = 100,
    UNSUPPORTED_DEVICE = 101,
    UNSUPPORTED_OS_VERSION = 102,
    FETCH_VIDEO_AD_NOT_CALLED = 103,
    VIDEO_AD_EXPIRED = 104,
    FETCHING_AD = 105,
    
    UNKNOWN_EXCEPTION_RAISED = 999,
} AdBuddizError;

@protocol AdBuddizDelegate <NSObject>

@optional

/*! @brief Called when an Ad has been downloaded and is ready to show. */
- (void)didCacheAd;

/*! @brief Called when an Ad has been displayed to user. */
- (void)didShowAd;

/*! 
 @brief Called when [AdBuddiz showAd] was called and SDK wasn't able to show an ad.
 @code
 - (void)didFailToShowAd:(AdBuddizError) error
 {
    NSLog(@"AdBuddizDelegate: didFailToShowAd : %i - %@", error, [AdBuddiz nameForError:error]);
 }
 @endcode
 @param AdBuddizError code explaining why
 */
- (void)didFailToShowAd:(AdBuddizError) error;

/*! @brief Called when a user clicked on an ad. */
- (void)didClick;

/*! @brief Called when a ad was hidden (user clicked on X or on the ad). */
- (void)didHideAd;

@end
