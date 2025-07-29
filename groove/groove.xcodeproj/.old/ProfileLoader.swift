//
//  ProfileLoader.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import Foundation

class ProfileLoader {
    static func loadProfile() -> UserProfile {
        guard let url = Bundle.main.url(forResource: "profile", withExtension: "json") else {
            fatalError("profile.json not found")
        }
        
        do {
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            return try decoder.decode(UserProfile.self, from: data)
            
        } catch {
            fatalError("Failed to decode profile.json: \(error)")
        }
    }
}
