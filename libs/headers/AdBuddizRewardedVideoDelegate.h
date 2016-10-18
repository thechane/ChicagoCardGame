//
//  AdBuddizRewardedVideoDelegate.h
//  Copyright (c) 2015 Purple Brain. All rights reserved.
//
#import "AdBuddizDelegate.h"

@protocol AdBuddizRewardedVideoDelegate <NSObject>

/*! @brief Called when an Ad has been displayed to user. */
- (void)didComplete;

@optional

/*! @brief Called when an Ad has been downloaded and is ready to show. */
- (void)didFetch;

/*! @brief Called when an Ad has been displayed to user. */
- (void)didNotComplete;

/*!
 @brief Called when [AdBuddiz.RewardedVideo show] was called and SDK wasn't able to show an ad.
 @code
 - (void)didFail:(AdBuddizRewardedVideoError) error
 {
 NSLog(@"AdBuddizRewardedVideoDelegate: didFail : %i - %@", error, [AdBuddiz nameForError:error]);
 }
 @endcode
 @param AdBuddizError code explaining why
 */
- (void)didFail:(AdBuddizError) error;

@end
