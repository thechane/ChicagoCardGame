//
//  AdBuddizRewardedVideo.h
//  Copyright (c) 2015 Purple Brain. All rights reserved.
//

#import <AdBuddiz/AdBuddizRewardedVideoDelegate.h>

@interface AdBuddizRewardedVideo : NSObject

/*!
 @brief Fetch an AdBuddiz Rewarded Video ad.
 @code
 [AdBuddiz.RewardedVideo fetch];
 @endcode
 @see http://publishers.adbuddiz.com/portal/support
 */
- (void)fetch;

/*!
 @brief Shows an AdBuddiz Rewarded Video ad.
 @code
 [AdBuddiz.RewardedVideo show];
 @endcode
 @see http://publishers.adbuddiz.com/portal/support
 */
- (void)show;

/*!
 @brief Returns YES if the SDK is ready to show an AdBuddiz Rewarded Video ad.
 @code
 if ([AdBuddiz.RewardedVideo isReadyToShow]) {
    [AdBuddiz.RewardedVideo show];
 }
 @endcode
 @note if you get YES, you're 100% sure that a show call will display an ad.
 @see http://publishers.adbuddiz.com/portal/support
 */
- (BOOL)isReadyToShow;

/*!
 @brief Provides the current User Id to the SDK.
 @code
 [AdBuddiz.RewardedVideo setUserId:@"uuid"];
 @endcode
 @see http://publishers.adbuddiz.com/portal/support
 */
- (void)setUserId:(NSString*)userId;

/*!
 @brief Sets AdBuddizRewardedVideoDelegate that will receive events callbacks.
 @code
 [AdBuddiz.RewardedVideo setDelegate:self];
 @endcode
 @param delegate, must implement <AdBuddizRewardedVideoDelegate> protocol
 @see http://publishers.adbuddiz.com/portal/support
 */
- (void)setDelegate:(id<AdBuddizRewardedVideoDelegate>)delegate;

/*!
 @brief Convert AdBuddizRewardedVideoError code to understandable NSString *.
 @code
 - (void)didFail:(AdBuddizRewardedVideoError) error
 {
 NSLog(@"AdBuddizRewardedVideoDelegate: didFail : %i - %@", error, [AdBuddiz.RewardedVideo nameForError:error]);
 }
 @endcode
 @param error, the AdBuddizRewardedVideoError code
 @see http://publishers.adbuddiz.com/portal/support
 */
- (NSString *)nameForError:(AdBuddizError)error;

@end