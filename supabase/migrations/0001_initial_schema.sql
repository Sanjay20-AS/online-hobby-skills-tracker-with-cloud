-- Initial schema for Online Hobby & Skills Tracker
-- Tables, relationships, indexes, RLS policies

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. PROFILES — Extended user information
-- ============================================================================

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    bio TEXT,
    avatar_url TEXT,
    visibility TEXT DEFAULT 'private' CHECK (visibility IN ('public', 'private')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE profiles IS 'User profiles with public/private visibility control';
COMMENT ON COLUMN profiles.username IS 'Unique identifier for user (immutable)';
COMMENT ON COLUMN profiles.visibility IS 'Controls whether profile is discoverable by other users (public/private)';

CREATE UNIQUE INDEX idx_profiles_username ON profiles(LOWER(username));
CREATE INDEX idx_profiles_visibility ON profiles(visibility);

-- ============================================================================
-- 2. HOBBIES — User hobbies
-- ============================================================================

CREATE TABLE IF NOT EXISTS hobbies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT hobby_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

COMMENT ON TABLE hobbies IS 'Hobbies owned by users';
COMMENT ON COLUMN hobbies.category IS 'Optional hobby category (e.g., art, music, sports)';

CREATE INDEX idx_hobbies_user_id ON hobbies(user_id);
CREATE INDEX idx_hobbies_created_at ON hobbies(created_at DESC);

-- ============================================================================
-- 3. SKILLS — Skills users want to develop or have developed
-- ============================================================================

CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    hobby_id UUID REFERENCES hobbies(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT,
    proficiency_level TEXT CHECK (proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT skill_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

COMMENT ON TABLE skills IS 'Skills owned by users; can be associated with hobbies';
COMMENT ON COLUMN skills.hobby_id IS 'Optional hobby this skill is related to';
COMMENT ON COLUMN skills.proficiency_level IS 'Skill proficiency level (beginner/intermediate/advanced/expert)';

CREATE INDEX idx_skills_user_id ON skills(user_id);
CREATE INDEX idx_skills_proficiency_level ON skills(proficiency_level);

-- ============================================================================
-- 4. GOALS — Learning or achievement goals
-- ============================================================================

CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    hobby_id UUID REFERENCES hobbies(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    target_date DATE,
    target_hours INTEGER,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT goal_title_not_empty CHECK (LENGTH(TRIM(title)) > 0),
    CONSTRAINT goal_target_hours_positive CHECK (target_hours IS NULL OR target_hours > 0)
);

COMMENT ON TABLE goals IS 'Goals associated with hobbies; enforces user ownership';
COMMENT ON COLUMN goals.target_date IS 'Target completion date (optional)';
COMMENT ON COLUMN goals.target_hours IS 'Target hours to invest (optional)';
COMMENT ON COLUMN goals.status IS 'Goal status: pending, in_progress, completed, or cancelled';

CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_goals_hobby_id ON goals(hobby_id);
CREATE INDEX idx_goals_status ON goals(status);

-- ============================================================================
-- 5. PRACTICE_SESSIONS — Tracking practice activities
-- ============================================================================

CREATE TABLE IF NOT EXISTS practice_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    hobby_id UUID NOT NULL REFERENCES hobbies(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    duration_minutes INTEGER NOT NULL,
    notes TEXT,
    session_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT practice_duration_positive CHECK (duration_minutes > 0)
);

COMMENT ON TABLE practice_sessions IS 'Practice session logs; user_id, hobby_id validated via RLS';
COMMENT ON COLUMN practice_sessions.duration_minutes IS 'Session duration in minutes';

CREATE INDEX idx_practice_sessions_user_id ON practice_sessions(user_id);
CREATE INDEX idx_practice_sessions_hobby_id ON practice_sessions(hobby_id);
CREATE INDEX idx_practice_sessions_skill_id ON practice_sessions(skill_id);
CREATE INDEX idx_practice_sessions_session_date ON practice_sessions(session_date DESC);

-- ============================================================================
-- 6. MILESTONES — Progress milestones
-- ============================================================================

CREATE TABLE IF NOT EXISTS milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    achieved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT milestone_title_not_empty CHECK (LENGTH(TRIM(title)) > 0)
);

COMMENT ON TABLE milestones IS 'Milestones within goals; user_id validated via RLS';

CREATE INDEX idx_milestones_user_id ON milestones(user_id);
CREATE INDEX idx_milestones_goal_id ON milestones(goal_id);
CREATE INDEX idx_milestones_achieved_at ON milestones(achieved_at);

-- ============================================================================
-- 7. UPLOADS — File metadata for user uploads
-- ============================================================================

CREATE TABLE IF NOT EXISTS uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    hobby_id UUID REFERENCES hobbies(id) ON DELETE SET NULL,
    original_filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT upload_original_filename_not_empty CHECK (LENGTH(TRIM(original_filename)) > 0),
    CONSTRAINT upload_storage_path_not_empty CHECK (LENGTH(TRIM(storage_path)) > 0),
    CONSTRAINT upload_file_size_positive CHECK (file_size > 0)
);

COMMENT ON TABLE uploads IS 'File upload metadata; actual files stored in Supabase Storage under user_id paths';
COMMENT ON COLUMN uploads.hobby_id IS 'Optional hobby this upload is associated with';
COMMENT ON COLUMN uploads.original_filename IS 'Original filename provided by user';
COMMENT ON COLUMN uploads.storage_path IS 'Path in Supabase Storage';

CREATE INDEX idx_uploads_user_id ON uploads(user_id);
CREATE INDEX idx_uploads_created_at ON uploads(created_at DESC);

-- ============================================================================
-- 8. POSTS — Community posts (hobbies, achievements, etc.)
-- ============================================================================

CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    hobby_id UUID REFERENCES hobbies(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT post_title_not_empty CHECK (LENGTH(TRIM(title)) > 0),
    CONSTRAINT post_content_not_empty CHECK (LENGTH(TRIM(content)) > 0)
);

COMMENT ON TABLE posts IS 'Community posts with public/private visibility; user_id validated via RLS';
COMMENT ON COLUMN posts.visibility IS 'Post visibility: public (all authenticated users) or private (owner only)';

CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_hobby_id ON posts(hobby_id);
CREATE INDEX idx_posts_visibility ON posts(visibility);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);

-- ============================================================================
-- 9. LIKES — Post interactions
-- ============================================================================

CREATE TABLE IF NOT EXISTS likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, post_id)
);

COMMENT ON TABLE likes IS 'Post likes; visibility and self-like prevention enforced via RLS';

CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_post_id ON likes(post_id);

-- ============================================================================
-- 10. COMMENTS — Post comments
-- ============================================================================

CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT comment_content_not_empty CHECK (LENGTH(TRIM(content)) > 0)
);

COMMENT ON TABLE comments IS 'Post comments; visibility enforced via RLS';

CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);

-- ============================================================================
-- 11. FOLLOWS — User follow relationships
-- ============================================================================

CREATE TABLE IF NOT EXISTS follows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    follower_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(follower_id, following_id),
    CONSTRAINT follow_not_self CHECK (follower_id != following_id)
);

COMMENT ON TABLE follows IS 'User follow relationships; prevents self-follows and duplicates';

CREATE INDEX idx_follows_follower_id ON follows(follower_id);
CREATE INDEX idx_follows_following_id ON follows(following_id);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all application-data tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE hobbies ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE practice_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE follows ENABLE ROW LEVEL SECURITY;

-- profiles: users see own profile, see public profiles
CREATE POLICY "profiles_self_update" ON profiles
    FOR UPDATE USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY "profiles_self_delete" ON profiles
    FOR DELETE USING (auth.uid() = id);

CREATE POLICY "profiles_select_self_or_public" ON profiles
    FOR SELECT USING (
        auth.uid() = id OR visibility = 'public'
    );

-- hobbies: users manage own, see owned, public users' hobbies
CREATE POLICY "hobbies_owner_all" ON hobbies
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "hobbies_select_public_user" ON hobbies
    FOR SELECT USING (
        user_id IN (SELECT id FROM profiles WHERE visibility = 'public')
    );

-- skills: users manage own, see owned, public users' skills
CREATE POLICY "skills_owner_all" ON skills
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "skills_select_public_user" ON skills
    FOR SELECT USING (
        user_id IN (SELECT id FROM profiles WHERE visibility = 'public')
    );

-- goals: users manage own only
CREATE POLICY "goals_owner_all" ON goals
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- practice_sessions: users manage own only
CREATE POLICY "practice_sessions_owner_all" ON practice_sessions
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- milestones: users manage own (via goal ownership)
CREATE POLICY "milestones_owner_all" ON milestones
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- uploads: users manage own only
CREATE POLICY "uploads_owner_all" ON uploads
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- posts: users manage own, see own or public
CREATE POLICY "posts_owner_all" ON posts
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "posts_select_own_or_public" ON posts
    FOR SELECT USING (
        auth.uid() = user_id OR visibility = 'public'
    );

-- likes: users manage own, see within visible posts
CREATE POLICY "likes_owner_delete_insert" ON likes
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "likes_owner_insert" ON likes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "likes_select_visible_posts" ON likes
    FOR SELECT USING (
        post_id IN (
            SELECT id FROM posts WHERE visibility = 'public' OR user_id = auth.uid()
        )
    );

-- comments: users manage own, see within visible posts
CREATE POLICY "comments_owner_all" ON comments
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "comments_select_visible_posts" ON comments
    FOR SELECT USING (
        post_id IN (
            SELECT id FROM posts WHERE visibility = 'public' OR user_id = auth.uid()
        )
    );

-- follows: users manage own follow relationships
CREATE POLICY "follows_follower_all" ON follows
    FOR ALL USING (auth.uid() = follower_id)
    WITH CHECK (auth.uid() = follower_id);

CREATE POLICY "follows_select_authenticated" ON follows
    FOR SELECT USING (auth.role() = 'authenticated');

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC PROFILE CREATION
-- ============================================================================

CREATE OR REPLACE FUNCTION create_profile_on_signup()
RETURNS TRIGGER AS $$
DECLARE
    generated_username TEXT;
    username_attempt TEXT;
    counter INT := 0;
BEGIN
    -- Generate initial username from email or user metadata
    IF NEW.raw_user_meta_data ? 'username' AND NEW.raw_user_meta_data->>'username' != '' THEN
        generated_username := LOWER(NEW.raw_user_meta_data->>'username');
    ELSIF NEW.email IS NOT NULL THEN
        generated_username := LOWER(SPLIT_PART(NEW.email, '@', 1));
    ELSE
        generated_username := 'user_' || SUBSTRING(NEW.id::TEXT, 1, 8);
    END IF;

    -- Ensure username is valid (alphanumeric + underscore, 3-30 chars)
    generated_username := REGEXP_REPLACE(generated_username, '[^a-z0-9_]', '_', 'g');
    generated_username := SUBSTRING(generated_username, 1, 30);
    IF LENGTH(generated_username) < 3 THEN
        generated_username := 'user_' || SUBSTRING(NEW.id::TEXT, 1, 8);
    END IF;

    username_attempt := generated_username;

    -- Handle username collisions by appending numbers
    WHILE EXISTS (SELECT 1 FROM public.profiles WHERE LOWER(username) = LOWER(username_attempt)) LOOP
        counter := counter + 1;
        IF counter > 100 THEN
            -- Fallback: use uuid if collision resolution fails
            username_attempt := 'user_' || SUBSTRING(NEW.id::TEXT, 1, 8);
            EXIT;
        END IF;
        username_attempt := generated_username || counter::TEXT;
    END LOOP;

    -- Insert profile with resolved username
    INSERT INTO public.profiles (id, username, visibility)
    VALUES (NEW.id, username_attempt, 'private')
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    -- Log error and re-raise to prevent silent failure
    RAISE WARNING 'Profile creation error for user %: %', NEW.id, SQLERRM;
    RAISE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = 'public';

CREATE TRIGGER trigger_create_profile_on_signup
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION create_profile_on_signup();

-- ============================================================================
-- TIMESTAMPS UPDATE TRIGGER
-- ============================================================================

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER trigger_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_hobbies_updated_at BEFORE UPDATE ON hobbies
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_skills_updated_at BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_goals_updated_at BEFORE UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_posts_updated_at BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- DATA INTEGRITY TRIGGERS
-- ============================================================================

-- Prevent users from liking their own posts
CREATE OR REPLACE FUNCTION prevent_self_like()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM posts 
        WHERE posts.id = NEW.post_id AND posts.user_id = NEW.user_id
    ) THEN
        RAISE EXCEPTION 'Users cannot like their own posts';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_self_like BEFORE INSERT ON likes
    FOR EACH ROW EXECUTE FUNCTION prevent_self_like();

-- Prevent comments on private posts by unauthorized users
CREATE OR REPLACE FUNCTION prevent_unauthorized_comment()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM posts 
        WHERE posts.id = NEW.post_id 
        AND posts.visibility = 'private' 
        AND posts.user_id != NEW.user_id
    ) THEN
        RAISE EXCEPTION 'Cannot comment on private posts of other users';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_unauthorized_comment BEFORE INSERT ON comments
    FOR EACH ROW EXECUTE FUNCTION prevent_unauthorized_comment();

-- Prevent likes on private posts by unauthorized users  
CREATE OR REPLACE FUNCTION prevent_unauthorized_like()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM posts 
        WHERE posts.id = NEW.post_id 
        AND posts.visibility = 'private' 
        AND posts.user_id != NEW.user_id
    ) THEN
        RAISE EXCEPTION 'Cannot like private posts of other users';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_unauthorized_like BEFORE INSERT ON likes
    FOR EACH ROW EXECUTE FUNCTION prevent_unauthorized_like();

-- ============================================================================
-- OWNERSHIP VALIDATION TRIGGERS
-- ============================================================================

-- Enforce that practice_sessions can only reference hobbies and skills owned by same user
CREATE OR REPLACE FUNCTION validate_practice_session_ownership()
RETURNS TRIGGER AS $$
BEGIN
    -- Check hobby belongs to user
    IF NOT EXISTS (SELECT 1 FROM hobbies WHERE id = NEW.hobby_id AND user_id = NEW.user_id) THEN
        RAISE EXCEPTION 'Practice session hobby must belong to same user';
    END IF;
    
    -- Check skill belongs to user (if provided)
    IF NEW.skill_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM skills WHERE id = NEW.skill_id AND user_id = NEW.user_id) THEN
        RAISE EXCEPTION 'Practice session skill must belong to same user';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_practice_session_ownership BEFORE INSERT OR UPDATE ON practice_sessions
    FOR EACH ROW EXECUTE FUNCTION validate_practice_session_ownership();

-- Enforce that goals can only reference hobbies owned by same user
CREATE OR REPLACE FUNCTION validate_goal_ownership()
RETURNS TRIGGER AS $$
BEGIN
    -- Check hobby belongs to user (if provided)
    IF NEW.hobby_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM hobbies WHERE id = NEW.hobby_id AND user_id = NEW.user_id) THEN
        RAISE EXCEPTION 'Goal hobby must belong to same user';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_goal_ownership BEFORE INSERT OR UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION validate_goal_ownership();

-- Enforce that milestones can only reference goals owned by same user
CREATE OR REPLACE FUNCTION validate_milestone_ownership()
RETURNS TRIGGER AS $$
BEGIN
    -- Check goal belongs to user
    IF NOT EXISTS (SELECT 1 FROM goals WHERE id = NEW.goal_id AND user_id = NEW.user_id) THEN
        RAISE EXCEPTION 'Milestone goal must belong to same user';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_milestone_ownership BEFORE INSERT OR UPDATE ON milestones
    FOR EACH ROW EXECUTE FUNCTION validate_milestone_ownership();

-- Enforce that posts can only reference hobbies owned by same user
CREATE OR REPLACE FUNCTION validate_post_ownership()
RETURNS TRIGGER AS $$
BEGIN
    -- Check hobby belongs to user (if provided)
    IF NEW.hobby_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM hobbies WHERE id = NEW.hobby_id AND user_id = NEW.user_id) THEN
        RAISE EXCEPTION 'Post hobby must belong to same user';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_post_ownership BEFORE INSERT OR UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION validate_post_ownership();

-- Enforce that uploads can only reference hobbies owned by same user
CREATE OR REPLACE FUNCTION validate_upload_ownership()
RETURNS TRIGGER AS $$
BEGIN
    -- Check hobby belongs to user (if provided)
    IF NEW.hobby_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM hobbies WHERE id = NEW.hobby_id AND user_id = NEW.user_id) THEN
        RAISE EXCEPTION 'Upload hobby must belong to same user';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_upload_ownership BEFORE INSERT OR UPDATE ON uploads
    FOR EACH ROW EXECUTE FUNCTION validate_upload_ownership();

-- Enforce private post access restrictions on UPDATE for comments
CREATE OR REPLACE FUNCTION validate_comment_visibility_on_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Check post visibility on UPDATE
    IF EXISTS (
        SELECT 1 FROM posts 
        WHERE posts.id = NEW.post_id 
        AND posts.visibility = 'private' 
        AND posts.user_id != NEW.user_id
    ) THEN
        RAISE EXCEPTION 'Cannot update comment on private posts of other users';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_comment_visibility_on_update BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION validate_comment_visibility_on_update();
