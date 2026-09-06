import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  User, 
  onAuthStateChanged, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signInWithPopup, 
  signOut as firebaseSignOut 
} from 'firebase/auth';
import { auth, googleProvider } from '../firebase';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  token: string | null;
  signInWithGoogle: () => Promise<void>;
  signInWithEmail: (email: string, pass: string) => Promise<void>;
  signUpWithEmail: (email: string, pass: string) => Promise<void>;
  logout: () => Promise<void>;
  setDevUser: (devUid: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Only auto-restore dev user if explicitly saved by user in current session
    const savedDevToken = sessionStorage.getItem('dev_token');
    if (savedDevToken) {
      const devUid = savedDevToken.replace('mock-user-', '');
      setUser({
        uid: devUid,
        email: `${devUid}@example.com`,
        displayName: `Candidate (${devUid})`,
      } as unknown as User);
      setToken(savedDevToken);
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        try {
          const idToken = await currentUser.getIdToken();
          setToken(idToken);
        } catch {
          setToken(null);
        }
      } else {
        setToken(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    const res = await signInWithPopup(auth, googleProvider);
    const idToken = await res.user.getIdToken();
    setToken(idToken);
  };

  const signInWithEmail = async (email: string, pass: string) => {
    const res = await signInWithEmailAndPassword(auth, email, pass);
    const idToken = await res.user.getIdToken();
    setToken(idToken);
  };

  const signUpWithEmail = async (email: string, pass: string) => {
    const res = await createUserWithEmailAndPassword(auth, email, pass);
    const idToken = await res.user.getIdToken();
    setToken(idToken);
  };

  const logout = async () => {
    sessionStorage.removeItem('dev_token');
    localStorage.removeItem('dev_token');
    await firebaseSignOut(auth).catch(() => {});
    setUser(null);
    setToken(null);
  };

  const setDevUser = (devUid: string) => {
    const mockToken = `mock-user-${devUid}`;
    sessionStorage.setItem('dev_token', mockToken);
    setToken(mockToken);
    setUser({
      uid: devUid,
      email: `${devUid}@example.com`,
      displayName: `Candidate (${devUid})`,
    } as unknown as User);
  };

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      token,
      signInWithGoogle,
      signInWithEmail,
      signUpWithEmail,
      logout,
      setDevUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
