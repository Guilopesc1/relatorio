import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import session, request
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from database import Database

class AuthManager:
    def __init__(self):
        self.db = Database()
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-this')
        self.token_expiry_hours = 24
    
    def create_user(self, email: str, password: str, name: str = None) -> Dict[str, Any]:
        """Cria um novo usuário no sistema"""
        try:
            # Verificar se usuário já existe
            existing_user = self.get_user_by_email(email)
            if existing_user:
                return {'success': False, 'message': 'Email já cadastrado'}
            
            # Hash da senha
            password_hash = generate_password_hash(password)
            
            # Inserir usuário
            response = self.db.supabase.table('auth_users').insert({
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'is_active': True
            }).execute()
            
            if response.data:
                return {'success': True, 'user': response.data[0]}
            else:
                return {'success': False, 'message': 'Erro ao criar usuário'}
                
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Autentica usuário com email e senha"""
        try:
            user = self.get_user_by_email(email)
            if not user:
                return {'success': False, 'message': 'Usuário não encontrado'}
            
            if not user.get('is_active'):
                return {'success': False, 'message': 'Usuário desativado'}
            
            # Verificar senha
            if check_password_hash(user['password_hash'], password):
                # Atualizar último login
                self.update_last_login(user['id'])
                
                # Gerar token JWT
                token = self.generate_jwt_token(user)
                
                return {
                    'success': True, 
                    'user': user,
                    'token': token
                }
            else:
                return {'success': False, 'message': 'Senha incorreta'}
                
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por email"""
        try:
            response = self.db.supabase.table('auth_users') \
                .select('*') \
                .eq('email', email) \
                .execute()
            
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por ID"""
        try:
            response = self.db.supabase.table('auth_users') \
                .select('*') \
                .eq('id', user_id) \
                .execute()
            
            return response.data[0] if response.data else None
        except Exception:
            return None
    
    def update_last_login(self, user_id: str):
        """Atualiza timestamp do último login"""
        try:
            self.db.supabase.table('auth_users') \
                .update({'last_login': datetime.now().isoformat()}) \
                .eq('id', user_id) \
                .execute()
        except Exception:
            pass
    
    def generate_jwt_token(self, user: Dict[str, Any]) -> str:
        """Gera token JWT para o usuário"""
        payload = {
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def store_facebook_token(self, user_id: str, access_token: str, expires_at: datetime = None, facebook_user_id: str = None):
        """Armazena tokens do Facebook OAuth"""
        try:
            update_data = {
                'facebook_access_token': access_token,
                'facebook_user_id': facebook_user_id
            }
            
            if expires_at:
                update_data['facebook_token_expires_at'] = expires_at.isoformat()
            
            self.db.supabase.table('auth_users') \
                .update(update_data) \
                .eq('id', user_id) \
                .execute()
                
            return True
        except Exception as e:
            print(f"Erro ao armazenar token Facebook: {e}")
            return False
    
    def store_google_token(self, user_id: str, access_token: str, refresh_token: str = None, expires_at: datetime = None, google_user_id: str = None):
        """Armazena tokens do Google OAuth"""
        try:
            update_data = {
                'google_access_token': access_token,
                'google_user_id': google_user_id
            }
            
            if refresh_token:
                update_data['google_refresh_token'] = refresh_token
            
            if expires_at:
                update_data['google_token_expires_at'] = expires_at.isoformat()
            
            self.db.supabase.table('auth_users') \
                .update(update_data) \
                .eq('id', user_id) \
                .execute()
                
            return True
        except Exception as e:
            print(f"Erro ao armazenar token Google: {e}")
            return False
    
    def get_facebook_token(self, user_id: str) -> Optional[str]:
        """Recupera token do Facebook para o usuário"""
        try:
            user = self.get_user_by_id(user_id)
            if user and user.get('facebook_access_token'):
                # Verificar se token não expirou
                if user.get('facebook_token_expires_at'):
                    expires_at = datetime.fromisoformat(user['facebook_token_expires_at'].replace('Z', '+00:00'))
                    if datetime.now() > expires_at:
                        return None
                
                return user['facebook_access_token']
            return None
        except Exception:
            return None
    
    def get_google_token(self, user_id: str) -> Optional[Dict[str, str]]:
        """Recupera tokens do Google para o usuário"""
        try:
            print(f"[DEBUG AUTH] Buscando tokens do Google para user_id: {user_id}")
            user = self.get_user_by_id(user_id)
            print(f"[DEBUG AUTH] Usuário encontrado: {user is not None}")
            
            if user and user.get('google_access_token'):
                tokens = {
                    'access_token': user['google_access_token'],
                    'refresh_token': user.get('google_refresh_token'),
                    'expires_at': user.get('google_token_expires_at')
                }
                print(f"[DEBUG AUTH] Tokens encontrados - Access: {tokens['access_token'][:20] if tokens['access_token'] else 'None'}...")
                print(f"[DEBUG AUTH] Refresh token: {'Sim' if tokens['refresh_token'] else 'Não'}")
                print(f"[DEBUG AUTH] Expira em: {tokens['expires_at']}")
                return tokens
            else:
                print(f"[DEBUG AUTH] Nenhum token Google encontrado para o usuário")
                return None
        except Exception as e:
            print(f"[DEBUG AUTH] Erro ao buscar tokens: {e}")
            return None
    
    def require_auth(self, f):
        """Decorator para proteger rotas que precisam de autenticação"""
        def decorated_function(*args, **kwargs):
            token = None
            
            # Verificar token no header Authorization
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]  # Remove "Bearer "
                except IndexError:
                    return {'error': 'Token inválido'}, 401
            
            # Verificar token na sessão
            elif 'auth_token' in session:
                token = session['auth_token']
            
            if not token:
                return {'error': 'Token de autenticação requerido'}, 401
            
            # Verificar token
            payload = self.verify_jwt_token(token)
            if not payload:
                return {'error': 'Token inválido ou expirado'}, 401
            
            # Adicionar dados do usuário ao request
            request.current_user = self.get_user_by_id(payload['user_id'])
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
